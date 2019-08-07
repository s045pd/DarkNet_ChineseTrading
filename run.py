import random
import re
import sys
import time
from base64 import b64encode
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup as bs_4

# import pudb;pu.db
import moment
import requests
import click
from pyquery import PyQuery as jq
from retry import retry
from io import BytesIO
from conf import Config
from task import telegram, logreport, telegram_withpic
from common import make_new_tor_id, random_key, init_path, fake_datas
from log import success, info, error, warning, debug
from parser import Parser
from cursor import Cursor
import nude


class DarkNet_ChineseTradingNetwork(object):
    def __init__(self, domain, just_update):
        self.domain = domain
        self.autim = 0
        self.sid = ""
        self.just_update = just_update
        self.notice_range = 0
        self.rootpath = "datas"
        self.screenpath = "screen_shot"
        list(map(init_path, [self.rootpath, self.screenpath]))
        self.init_domain()
        self.session = self.new_session()

    def init_domain(self):
        last_domain = Cursor.get_last_domain()
        self.domain = last_domain if last_domain else self.domain
        self.make_links()

    def new_session(self):
        new_session = requests.Session()
        new_session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }
        new_session.proxies = {"https": Config.tor_proxy, "http": Config.tor_proxy}
        new_session.timeout = 30
        new_session.verify = False
        return new_session

    def refresh_new_target(self, resp):
        warning("refresh checking")
        next_path = Parser.get_next_target(resp)
        self.sid = Parser.get_sid(resp, self.sid)

        if next_path:
            parse_res = urlparse(next_path)
            domain = parse_res.netloc
            query = parse_res.query
            if domain and self.domain != domain:
                self.domain = domain
                info(f"find new domain: {self.domain}")
                Cursor.create_new_domain(self.domain)

            if query:
                query = dict((item.split("=") for item in query.split("&")))
                if "autim" in query:
                    self.autim = int(query["autim"])
                    info(f"autim: {self.autim}")

            self.make_links()
            next_url = urljoin(resp.url, next_path)
            warning(f"refresh to: {next_url}")
            return self.refresh_new_target(self.session.get(next_url))
        return resp

    def make_links(self):
        self.main_url = f"http://{self.domain}/"
        self.index_url = f"{self.main_url}/index.php"

    def report_cookies(self):
        [success(f"{key}:{value}") for key, value in self.session.cookies.items()]

    def to_main_page(self):
        warning(f"fetch main page: {self.main_url}")
        resp = self.session.get(self.main_url)
        return resp

    def clear_cookies(self):
        self.session.cookies.clear()
        info(f"already cleaned session cookies.")

    def clean_log(self, resp, lens=100):
        return (" ".join(bs_4(resp.text, "lxml").text.split()))[:lens] + "..."

    def create_random_author(self):
        self.usr = fake_datas()
        self.pwd = random_key(random.randint(10, 16))

        info(f"usr: {self.usr} pwd: {self.pwd}")

    def get_pic_base64(self, link):
        return (
            link if "http" not in link else bytes.decode(b64encode(self.get_pic(link)))
        )

    def get_cookie_string(self):
        cookie_name_space = [
            "PHPSESSID",
            "phpbb3_nspa_c",
            "phpbb3_nspa_a",
            "phpbb3_nspa_u",
            "phpbb3_nspa_k",
            "phpbb3_nspa_sid",
        ]
        strs = "; ".join(
            map(
                lambda name: f"{name}={self.session.cookies.get(name,'',self.domain)}",
                cookie_name_space,
            )
        )
        debug(f"cookies string: {strs}")
        return strs

    def update_random_user(self):
        user = Cursor.get_random_user()
        if user or True:
            self.usr = user.user
            self.pwd = user.pwd
            return True

    @retry()
    def get_pic(self, link):
        return self.session.get(link).content

    def save_pics(self, urls, sid):
        image_box = []
        for index, url in enumerate(urls):
            url = url if "http" in url else urljoin(f"http://{self.domain}", url)
            info(f"---fetch pic[{index}]:{url}")
            path = f"{self.screenpath}/{sid}_{index}.png"
            current_image = None
            with open(path, "wb") as file:
                current_image = self.get_pic(url)
                file.write(current_image)
                success(f"image saved: {path}")
            if Config.no_porn_img and nude.is_nude(path):
                warning("nude detected")
                continue
            image_box.append(BytesIO(current_image))
        return image_box

    @retry(delay=2, tries=20)
    def first_fetch(self):
        try:
            warning(f"domain: {self.domain}")
            self.clear_cookies()
            self.autim, self.sid, self.login_payload, self.login_url, self.register_url = Parser.get_login_and_reg_payload(
                self.refresh_new_target(self.to_main_page())
            )  # / -> ucp.php
            self.report_cookies()
            if not self.update_random_user():  # or random.choice([1, 0]):
                self.register()
            return True
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            raise e

    def make_reg_headers(self, resp):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": self.main_url,
            "Referer": resp.url,
        }

    @retry(delay=2, tries=10)
    def register(self):
        try:
            warning("register confirm")
            resp = self.refresh_new_target(
                self.session.get(
                    self.register_url,
                    headers={
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Referer": self.register_url,
                    },
                )
            )
            token, creation_time = Parser.get_token_and_creation_time(resp)
            warning("start register")
            resp = self.session.post(
                self.register_url,
                data={
                    "agreed": "===好的,我已明白,请跳转到下一页继续注册====",
                    "autim": self.autim,
                    "change_lang": "",
                    "creation_time": creation_time,
                    "form_token": token,
                },
                headers=self.make_reg_headers(resp),
            )
            token, creation_time = Parser.get_token_and_creation_time(resp)
            confirm_code, confirm_id = Parser.get_captcha(self.get_pic, resp)
            self.create_random_author()
            data = {
                "username": self.usr,
                "new_password": self.pwd,
                "password_confirm": self.pwd,
                "email": "xxxx@xxxx.xxx",
                "lang": "zh_cmn_hans",
                "tz_date": "UTC+08:00 - Antarctica/Casey - "
                + moment.now().format("YYYY-MM-DD HH:mm"),
                "tz": "Asia/Hong_Kong",
                "agreed": "true",
                "change_lang": "0",
                "confirm_code": confirm_code,
                "confirm_id": [confirm_id, confirm_id],
                "creation_time": creation_time,
                "form_token": token,
                "submit": " 用户名与密码已填好, 点此提交 ",
                "autim": self.autim,
            }
            resp = self.session.post(
                self.register_url, data=data, headers=self.make_reg_headers(resp)
            )
            assert "感谢注册" in resp.text
            success("register success")
            Cursor.create_new_user({"user": self.usr, "pwd": self.pwd})
        except KeyboardInterrupt:
            exit()
        except AssertionError as e:
            error("register failed")
            error(self.clean_log(resp))
            raise e

    @retry(delay=2, tries=10)
    def login(self):
        try:
            """
                ### 再次尝试
                1.因为网络问题重试

                ### 重新注册
                2.因为账户被封重试
                3.因为账户认证错误重试
            """
            warning(f"login -> [{self.usr}:{self.pwd}]")
            self.login_payload.update({"password": self.pwd, "username": self.usr})
            resp = self.session.post(
                self.login_url,
                data=self.login_payload,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Referer": f"http://{self.domain}/ucp.php?mode=login&autim={self.autim}",
                },
                allow_redirects=False,
            )
            debug(f"login[1] requests header: {resp.request.headers}")
            debug(f"login[1] response header: {resp.headers}")
            if resp.status_code == 302 and "Location" in resp.headers:
                resp = self.refresh_new_target(
                    self.session.get(
                        resp.headers.get("Location"),
                        headers={
                            "Referer": f"http://{self.domain}/ucp.php?mode=login&sid={self.sid}",
                            "Cookie": self.get_cookie_string(),
                        },
                    )
                )
            else:
                Cursor.ban_user(self.usr)
                return
            debug(f"login[2] requests header: {resp.request.headers}")
            debug(f"login[2] response header: {resp.headers}")
            if self.usr in resp.text and "暗网欢迎您" in resp.text:
                success("Auth Success")
                self.types = Parser.get_current_type(resp)
            else:
                error(f"Auth Faild: {self.clean_log(resp)}")
                if re.findall("已被封禁|无效的|违规被处理", resp.text):
                    Cursor.ban_user(self.usr)
                    if not self.register():
                        return
                    else:
                        raise ValueError
        except KeyboardInterrupt:
            exit()

    @retry(delay=2, tries=10)
    def get_type_datas(self, qeaid, name, page=1):
        url = f"{self.main_url}/pay/user_area.php?q_ea_id={qeaid}&pagey={page}#pagey"
        warning(f"get_type_datas: {url}")
        resp = self.session.get(
            url,
            headers={
                "Referer": f"http://{self.domain}/pay/user_area.php?q_ea_id={qeaid}",
                "Cookie": self.get_cookie_string(),
            },
        )
        resp.encoding = "utf8"
        hasres = False
        try:
            self.check_if_need_relogin(resp)
            for item, details_url in Parser.get_types(resp):
                self.get_details(
                    details_url,
                    Parser.get_type_datas(item),
                    name,
                    page,
                    Parser.get_index(item),
                    resp.url,
                )
                hasres = True
            if page == 1:
                return Parser.get_max_page(resp, self.just_update)
            if hasres:
                return True
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            error(f"get_type_datas: {e}")
            error(self.clean_log(resp))

    def check_if_need_relogin(self, resp, passed=False, need_raise=True):

        if passed or "缓存已经过期" in resp.text:
            """
                登录超时重新登录
            """
            debug("cache timeout!")
            if self.first_fetch():
                self.login()

        elif "您必须注册并登录才能浏览这个版面" in resp.text or "无效的用户名" in resp.text:
            """
                账户遭到封锁重新注册
            """
            self.register()
        else:
            return True

        if need_raise:
            raise ValueError

    @retry(delay=2, tries=10)
    def get_details(self, url, muti, name, page, index_str, referer_url):
        resp = self.session.get(
            url, headers={"Referer": referer_url, "Cookie": self.get_cookie_string()}
        )
        resp.encoding = "utf8"
        if not self.check_if_need_relogin(resp):
            return

        bs_data = bs_4(resp.text, "lxml")
        uid, sid = Parser.get_uid_and_sid(bs_data)

        if not any((uid, sid)):
            return

        details, person, notice, img = Cursor.get_model_details(uid, sid)
        try:
            person_datas, username = Parser.get_person_data(bs_data)
            if not person:
                person_datas.update(
                    {
                        "uid": uid,
                        "user": username,
                        "regtime": Parser.get_reg_date(bs_data, "1999-01-01"),
                    }
                )
                person = Cursor.create_person(person_datas)

            else:
                Cursor.update_person(person_datas, uid)
                person = person[0].uid

            if not notice:
                notice = Cursor.create_notice({"sid": sid})
            else:
                notice = notice[0].sid

            detailImages = None
            detailContent = Parser.get_detail_content(bs_data)
            if not img:
                urls = Parser.get_img_urls(bs_data)
                img = Cursor.create_img(
                    {"sid": sid, "img": urls, "detail": detailContent}
                )
                detailImages = self.save_pics(urls, sid)
            else:
                img = img[0].sid
            current_year = moment.now().year
            real_up_time = Parser.get_up_time(bs_data, current_year)
            details_datas = Parser.get_details(
                bs_data, current_year, real_up_time, muti
            )
            if not details:
                details_datas.update(
                    {
                        "sid": sid,
                        "user": person,
                        "area": muti["area"],
                        "title": muti["title"],
                        "detailurl": url,
                        "img": img,
                        "notice": notice,
                    }
                )
                details = Cursor.create_details(details_datas)
                self.make_msg(details, detailContent, detailImages, sid, username)
            else:
                Cursor.update_details(details_datas, sid)

            short_msg = f'[{name}:{page}:{index_str}]-{real_up_time}- {muti["title"]}'
            success(short_msg) if not details else warning(short_msg)

        except KeyboardInterrupt:
            exit()
        except Exception as e:
            error(f"[run-->__get_details]: {e}")
            # raise e

    def make_msg(self, details, content, imgs, sid, username):
        msg = f"{details.uptime}\n🔥{details.title}\n\nAuthor: {username}\nPrice: ${details.priceUSDT}\nSource: {details.detailurl}\n\n\n${content}\n"
        msg = msg if len(msg) < 1000 else msg[:997] + "..."
        if (
            details.area in Config.filterArea
            and moment.date(details.uptime)
            > moment.now()
            .replace(hours=0, minutes=0, seconds=0)
            .add(days=self.notice_range)
        ) or Config.sendForTest:
            if not imgs:
                # telegram.delay(msg, sid, Config.darknetchannelID)
                telegram(msg, sid, Config.darknetchannelID)
            else:
                telegram_withpic(imgs[0], msg, sid, Config.darknetchannelID)

    def run(self):
        while True:
            try:
                make_new_tor_id()
                self.check_if_need_relogin(None, True, False)
                for qeaid, name in self.types.items():
                    max_page = self.get_type_datas(qeaid, name)
                    for page in range(2, max_page):
                        if not self.get_type_datas(qeaid, name, page):
                            break
            except KeyboardInterrupt:
                exit()
            finally:
                time.sleep(1)


@click.command()
@click.option("--debug", is_flag=True, help="Print debug log")
@click.option(
    "--domain",
    default="deepmixaasic2p6vm6f4d4g52e4ve6t37ejtti4holhhkdsmq3jsf3id.onion",
    help="Target domain.",
)
@click.option(
    "--update", is_flag=True, help="Whether it has only been updated to crawl"
)
def main(debug, domain, update):
    Config.debug = debug
    DarkNet_ChineseTradingNetwork(domain, update).run()


if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            error(f"sleeping")
            logreport.delay(str(e))
            time.sleep(60)
