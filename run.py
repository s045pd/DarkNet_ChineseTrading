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
from common import make_new_tor_id, random_key, init_path
from log import success, info, error, warning, debug
from parser import Parser
from cursor import Cursor


class DarkNet_ChineseTradingNetwork(object):
    def __init__(self, domain, need_save_error, just_update):
        self.__domain = domain
        self.__autim = 0
        self.__sid = ""
        self.__need_save_error = need_save_error
        self.__just_update = just_update
        self.__notice_range = 0
        self.__rootpath = "datas"
        self.__screenpath = "screen_shot"

        list(map(init_path, [self.__rootpath, self.__screenpath]))
        self.__init_domain()
        self.session = self.__new_session()

    def __init_domain(self):
        last_domain = Cursor.get_last_domain()
        self.__domain = last_domain if last_domain else self.__domain
        self.__make_links()

    def __new_session(self):
        new_session = requests.Session()
        new_session.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0",
        }
        new_session.proxies = {"https": Config.tor_proxy, "http": Config.tor_proxy}
        new_session.timeout = 30
        return new_session

    def __refresh_new_target(self, resp):
        warning("Refresh Checking")
        Parser.get_next_target
        next_path = Parser.get_next_target(resp)
        self.__sid = Parser.get_sid(resp, self.__sid)

        if next_path:
            parse_res = urlparse(next_path)
            domain = parse_res.netloc
            query = parse_res.query
            if domain and self.__domain != domain:
                self.__domain = domain
                info(f"Find New Domain: {self.__domain}")
                Cursor.create_new_domain(self.__domain)

            if query:
                query = dict((item.split("=") for item in query.split("&")))
                if "autim" in query:
                    self.__autim = int(query["autim"])
                    info(f"autim: {self.__autim}")

            self.__make_links()
            next_url = urljoin(resp.url, next_path)
            warning(f"Refresh To: {next_url}")
            return self.__refresh_new_target(self.session.get(next_url))
        return resp

    def __make_links(self):
        self.__main_url = f"http://{self.__domain}/"
        self.__index_url = f"{self.__main_url}/index.php"

    def __report_cookies(self):
        [success(f"{key}:{value}") for key, value in self.session.cookies.items()]

    def __to_main_page(self):
        warning(f"Fetch Main Page: {self.__main_url}")
        resp = self.session.get(self.__main_url)
        return resp

    def __clear_cookies(self):
        self.session.cookies.clear()
        info(f"Already Cleaned Session Cookies.")

    def __clean_log(self, resp, lens=100):
        return (" ".join(bs_4(resp.text, "lxml").text.split()))[:lens] + "..."

    def __create_random_author(self):
        self.usr = random_key(12)
        self.pwd = random_key()
        info(f"usr: {self.usr} pwd: {self.pwd}")

    def __get_pic_base64(self, link):
        return (
            link
            if "http" not in link
            else bytes.decode(b64encode(self.__get_pic(link)))
        )

    @retry()
    def __get_pic(self, link):
        return self.session.get(link).content

    def __save_pics(self, urls, sid):
        imageBox = []
        for index, url in enumerate(urls):
            url = url if "http" in url else urljoin(f"http://{self.__domain}", url)
            info(f"---fetch PIC[{index}]:{url}")
            with open(f"{self.__screenpath}/{sid}_{index}.png", "wb") as imgfile:
                singelPIC = self.__get_pic(url)
                imgfile.write(singelPIC)
                imageBox.append(BytesIO(singelPIC))
        return imageBox

    @retry(delay=2, tries=20)
    def __first_fetch(self):
        try:

            warning(f"Domain: {self.__domain}")
            self.__clear_cookies()
            self.__autim, self.__sid, self.__login_payload, self.__login_url, self.__reg_url = Parser.get_login_and_reg_payload(
                self.__refresh_new_target(self.__to_main_page())
            )  # / -> ucp.php
            self.__report_cookies()
            user = Cursor.get_random_user()
            if not user:
                self.__reg()
            else:
                self.usr = user.user
                self.pwd = user.pwd
                if random.choice([1, 0, 0, 0, 0]):  # 佛系注册堆积账号池
                    self.__reg()
            return True
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            raise e

    def __make_reg_headers(self, resp):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": self.__main_url,
            "Pragma": "no-cache",
            "Referer": resp.url,
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0",
        }

    @retry(delay=2, tries=10)
    def __reg(self):
        try:
            warning("Reg Confirm")
            resp = self.__refresh_new_target(
                self.session.get(
                    self.__reg_url,
                    headers={
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Pragma": "no-cache",
                        "Referer": self.__reg_url,
                        "Upgrade-Insecure-Requests": "1",
                        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0",
                    },
                )
            )
            token, creation_time = Parser.get_token_and_creation_time(resp)
            warning("Start Reg")
            resp = self.session.post(
                self.__reg_url,
                data={
                    "agreed": "===好的,我已明白,请跳转到下一页继续注册====",
                    "autim": self.__autim,
                    "change_lang": "",
                    "creation_time": creation_time,
                    "form_token": token,
                },
                headers=self.__make_reg_headers(resp),
            )
            token, creation_time = Parser.get_token_and_creation_time(resp)
            confirm_code, confirm_id = Parser.get_captcha(self.__get_pic, resp)
            self.__create_random_author()
            data = {
                "agreed": "true",
                "autim": self.__autim,
                "change_lang": "0",
                "confirm_code": confirm_code,
                "confirm_id": [confirm_id, confirm_id],
                "creation_time": creation_time,
                "email": "xxxx@xxxx.xxx",
                "form_token": token,
                "lang": "zh_cmn_hans",
                "new_password": self.pwd,
                "password_confirm": self.pwd,
                "submit": " 用户名与密码已填好,+点此提交 ",
                "tz": "Asia/Hong_Kong",
                "tz_date": "UTC+08:00+-+Asia/Brunei+-+"
                + moment.now().format("DD+MM月+YYYY,+HH:mm"),
                "username": self.usr,
            }
            resp = self.session.post(
                self.__reg_url, data=data, headers=self.__make_reg_headers(resp)
            )
            assert "感谢注册" in resp.text
            success("Reg success！")
            Cursor.create_new_user({"user": self.usr, "pwd": self.pwd})
        except KeyboardInterrupt:
            exit()
        except AssertionError as e:
            error("Reg failed！")
            error(self.__clean_log(resp))
            self.__save_error("__reg.html", resp)
            raise e


    @retry(delay=2, tries=10)
    def __login(self):
        try:
            """
                ### 再次尝试
                1.因为网络问题重试

                ### 重新注册
                2.因为账户被封重试
                3.因为账户认证错误重试
            """
            warning(f"Login -> [{self.usr}:{self.pwd}]")
            self.__login_payload.update({"password": self.pwd, "username": self.usr})
            resp = self.__refresh_new_target(
                self.session.post(
                    self.__login_url,
                    data=self.__login_payload,
                    verify=False,
                    timeout=120,
                )
            )
            debug(resp.history)
            debug(resp.request.headers)
            debug(resp)
            if self.usr in resp.text and "暗网欢迎您" in resp.text:
                success("Auth Success")
                self.types = Parser.get_current_type(resp)
            else:
                error(f"Auth Faild: {self.__clean_log(resp)}")
                self.__save_error("__login.html", resp)
                if re.findall("已被封禁|无效的|违规被处理",resp.text):
                    Cursor.ban_user(self.usr)
                    if not self.__reg():
                        return
                    else:
                        raise ValueError
        except KeyboardInterrupt:
            exit()

    def __save_error(self, filename, resp):
        if not self.__need_save_error:
            return
        fullfilepath = f"{self.__rootpath}/{filename}"
        info(f"Html Log Saved to {fullfilepath}")
        with open(fullfilepath, "w") as f:
            f.write(resp.text)

    @retry(delay=2, tries=10)
    def __get_type_datas(self, qeaid, name, page=1):
        url = f"{self.__main_url}/pay/user_area.php?q_ea_id={qeaid}&pagey={page}#pagey"
        warning(url)
        resp = self.session.get(url)
        resp.encoding = "utf8"
        hasres = False
        try:
            self.__check_if_need_relogin(resp)
            self.__save_error(f"{qeaid}_{name}_{page}.html", resp)
            for item, details_url in Parser.get_types(resp):
                self.__get_details(
                    details_url,
                    Parser.get_type_datas(item),
                    name,
                    page,
                    Parser.get_index(item),
                )
                hasres = True
            if page == 1:
                return Parser.get_max_page(resp, self.__just_update)
            if hasres:
                return True
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            error(f"__get_type_datas: {e}")
            error(self.__clean_log(resp))
            # raise

    def __check_if_need_relogin(self, resp, passed=False, need_raise=True):

        if passed or "缓存已经过期" in resp.text:
            """
                登录超时重新登录
            """
            debug("Cache Timeout!")
            if self.__first_fetch():
                self.__login()

        elif "您必须注册并登录才能浏览这个版面" in resp.text or "无效的用户名" in resp.text:
            """
                账户遭到封锁重新注册
            """
            debug("User Blocked!")
            self.__reg()

        elif "您输入的确认码不正确" in resp.text:
            # elif "您的回答不正确" in resp.text:

            debug("Answer Error!")
            time.sleep(20)
            self.__reg()
        else:
            return True

        if need_raise:
            raise ValueError

    @retry(delay=2, tries=10)
    def __get_details(self, url, muti, name, page, index_str):
        resp = self.session.get(url)
        resp.encoding = "utf8"
        if not self.__check_if_need_relogin(resp):
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
                detailImages = self.__save_pics(urls, sid)
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
                self.__make_msg(details, detailContent, detailImages, sid, username)
            else:
                Cursor.update_details(details_datas, sid)

            short_msg = f'[{name}:{page}:{index_str}]-{real_up_time}- {muti["title"]}'
            success(short_msg) if not details else warning(short_msg)

        except KeyboardInterrupt:
            exit()
        except Exception as e:
            error(f"[run-->__get_details]: {e}")
            self.__save_error("__get_details.html", resp)
            # raise e

    def __make_msg(self, details, content, imgs, sid, username):

        msg = f"{details.uptime}\n🔥{details.title}\n\nAuthor: {username}\nPrice: ${details.priceUSDT}\nSource: {details.detailurl}\n\n\n${content}\n"
        msg = msg if len(msg) < 1000 else msg[:997] + "..."
        if (
            details.area in Config.filterArea
            and moment.date(details.uptime)
            > moment.now()
            .replace(hours=0, minutes=0, seconds=0)
            .add(days=self.__notice_range)
        ) or Config.sendForTest:
            if not imgs:
                # telegram.delay(msg, sid, Config.darknetchannelID)
                telegram(msg, sid, Config.darknetchannelID)
            else:
                telegram_withpic(imgs[0], msg, sid, Config.darknetchannelID)

    def Run(self):
        while True:
            try:
                make_new_tor_id()
                self.__check_if_need_relogin(None, True, False)
                for qeaid, name in self.types.items():
                    max_page = self.__get_type_datas(qeaid, name)
                    for page in range(2, max_page):
                        if not self.__get_type_datas(qeaid, name, page):
                            break
            except KeyboardInterrupt:
                exit()
            finally:
                time.sleep(1)


@click.command()
@click.option("--debug", is_flag=True, help="Print debug log")
@click.option(
    "--domain",
    default="vdh5nrnu7zsis7n2orxft3ax4oamhbtyzcb7srs73xj5t5rxiadavzyd.onion",
    help="Target domain.",
)
@click.option("--save_error", is_flag=True, help="Whether to save the error log")
@click.option(
    "--update", is_flag=True, help="Whether it has only been updated to crawl"
)
def main(debug, domain, save_error, update):

    Config.debug = debug
    DarkNet_ChineseTradingNetwork(domain, save_error, update).Run()


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
