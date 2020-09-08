import platform
import random
import re
import sys
import time
from base64 import b64encode
from dataclasses import dataclass
from io import BytesIO
from parser import Parser
from urllib.parse import urljoin

import click
import moment
import nude
import requests_html
from imgcat import imgcat
from peewee import IntegrityError, fn
from requests import RequestException
from retry import retry

from common import init_path, make_new_tor_id, random_key
from conf import Config
from cursor import Cursor
from exception import *
from log import *
from task import logreport, telegram, telegram_with_pic


@dataclass
class DarkNet_ChineseTradingNetwork(object):
    is_login = False
    domain = random.choice(Config.domains)
    proxies = {"http": Config.tor_proxy, "https": Config.tor_proxy}

    def __post__init__(self):
        ...

    def new_session(self):
        session = requests_html.HTMLSession()
        session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Host": self.domain,
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }
        session.timeout = 30
        session.verify = False
        self.session = session

    def get(self, path: str, params: dict = None, **kwargs):
        resp = self.session.get(
            urljoin(self.index_url, path), params=params, proxies=self.proxies, **kwargs
        )
        resp.encoding = "utf8"
        return resp

    def post(self, path, data: dict = None, json: dict = None, **kwargs):
        resp = self.session.post(
            urljoin(self.index_url, path),
            data=data,
            json=json,
            proxies=self.proxies,
            **kwargs,
        )
        resp.encoding = "utf8"
        return resp

    def load_main_page(self):
        resp = self.get(self.index_url)
        captcha_path = resp.html.find("img")[0].attrs["src"]
        form_path = resp.html.find("form")[0].attrs["action"]
        resp = self.post(
            form_path,
            data={
                "sub_code": Parser.predict_captcha(self.get, captcha_path),
                "lgsub": "进入下一步",
            },
        )

    def report_cookies(self):
        [success(f"{key}:{value}") for key, value in self.session.cookies.items()]

    def clean_lines(self, resp, lens=100):
        return (" ".join(resp.html.text.split()))[:lens] + "..."

    def update_random_user(self):
        self.auth = tuple([])
        if (user := Cursor.get_random_user()) :
            self.auth = (user.usr, user.pwd)
            info(f"随机用户: {self.auth=}")
            return True

    @retry((RequestException), delay=1)
    def get_pic(self, link):
        if not link:
            return ""
        warning(link)
        return self.get(link).content

    def save_pics(self, context, sid):
        image_box = []
        for indexs, img in enumerate(context["img"]):
            try:
                path = Config.screen_path / f"{sid}_{indexs}.png"
                with path.open("wb") as pic:
                    pic.write(img)
                    success(f"saved {path=}")
                if Config.no_porn_img and nude.is_nude(path):
                    warning(f"[{indexs}]nude detected")
                    continue
                image_box.append(path)
            except Exception as e:
                error(e)
        success(f"images: {len(image_box)}")
        context["img"] = image_box

    # @retry(delay=2, tries=10)
    def register(self):
        pwd = random_key(random.randint(10, 16))
        resp = self.post(
            "/entrance/registers.php",
            data={
                "regpass": pwd,
                "regpasss": pwd,
                "sub_code": Parser.predict_captcha(self.get),
                "regsub": "提交注册",
            },
        )
        if not (user_id_list := resp.html.search(" 用户编号: {} ")):
            error("注册失败")
            return

        self.auth = (user_id_list[0], pwd)
        success(f"注册成功: {self.auth}")

        Cursor.create_new_user(self.auth)

    @retry((RequestException, ValueError), tries=2, delay=10)
    def login(self):
        if len(self.auth) != 2:
            return
        resp = self.post(
            "/entrance/logins.php",
            data={
                "lgid": self.auth[0],
                "lgpass": self.auth[1],
                "sub_code": Parser.predict_captcha(self.get),
                "lgsub": "进入系统",
            },
        )
        if "注销" not in resp.text:
            error(f"{self.auth=}登录失败")
            raise ValueError("登录失败")
        success(f"{self.auth=}登录成功")
        self.is_login = True

    def make_msg(self, obj, context, sid, author):
        imgs = context["img"]
        warning(f"send msg [{sid}] img: [{len(imgs) if imgs else 0}]")
        msg = f"{obj.uptime}\n🔥{obj.title}\n\nAuthor: {author}\nPrice: ${obj.priceUSDT}\nSource: {obj.link}\n\n\n>>> {obj.text}\n"
        msg = msg if len(msg) < 1000 else msg[:997] + "..."
        if (
            moment.date(obj.uptime)
            > moment.now()
            .replace(hours=0, minutes=0, seconds=0)
            .add(days=abs(Config.notice_range_days) * -1)
        ) or Config.send_for_test:
            if not imgs:
                telegram(msg, sid, Config.tg_channel_id_darknet)
            else:
                telegram_with_pic(imgs, msg, sid, Config.tg_channel_id_darknet)

    @retry((RequestException), delay=1)
    def get_all_types(self):
        if not self.is_login:
            return
        for self.current_types in Config.filter_area:
            for page in range(2, self.get_singel_type()):
                self.get_singel_type(page)

    @retry((RequestException), delay=1)
    def get_singel_type(self, page=1):
        if not self.is_login:
            return
        path = self.current_types[0] + f"&pagea={page}#pagea"
        resp = self.get(path)
        for href, datas in Parser.parse_summary(resp):
            success(f'[{page}]: {datas["title"]}')
            self.get_singel_type_details(href, datas)
        if page == 1:
            return Parser.parse_max_page(resp, Config.just_update)

    @retry((RequestException), delay=1)
    def get_singel_type_details(self, path, datas):
        if not self.is_login:
            return

        sid, uid, resp = datas["sid"], datas["user"], self.get(path)
        new_data, imgs = Parser.parse_details(resp, self.get_pic, self.current_types[1])
        datas.update(new_data)
        info(f"{datas=}")
        obj = Cursor.get_model_details(sid)
        try:
            if not obj:
                obj = Cursor.create_details(datas)
                self.save_pics(imgs, sid)
                self.make_msg(obj, imgs, sid, uid)
            else:
                Cursor.update_details(datas, sid)

            short_msg = (
                f'[{self.current_types[1]}]-{datas["lasttime"]}- {datas["title"]}'
            )
            success(short_msg) if not obj else warning(short_msg)

        except KeyboardInterrupt:
            exit()
        except Exception as e:
            error(e)
            raise e

    def run(self):
        info(f"{self.domain=}")
        self.index_url = f"http://{self.domain}"
        make_new_tor_id()
        self.new_session()
        if not self.update_random_user():
            self.register()
        self.login()
        self.get_all_types()


if __name__ == "__main__":
    while True:
        try:
            DarkNet_ChineseTradingNetwork().run()
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            error(f"sleeping: {e}")
            logreport.delay(str(e))
            time.sleep(1)
            # raise e
