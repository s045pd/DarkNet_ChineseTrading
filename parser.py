import platform
import re
from io import BytesIO
from urllib.parse import urljoin, urlparse

import moment
import pytesseract
from bs4 import BeautifulSoup as bs_4
from imgcat import imgcat
from PIL import Image

from common import fix_nums, float_format
from log import debug, error, info


class Parser:
    @staticmethod
    def get_next_target(resp):
        try:
            next_target = re.findall(
                '<meta http-equiv="refresh" content="3;url=(.*?)">', resp.text
            )
            if next_target:
                info(f"Find Next Target: {next_target[0]}")
                return next_target[0]
        except Exception as e:
            error(f"[Parser->get_next_target]: {e}")

    @staticmethod
    def get_login_and_reg_payload(resp):
        try:
            if "500 Internal Privoxy Error" in resp.text:
                error("Check Your Proxy")
                exit()
            bs_data = bs_4(resp.text, "lxml")
            autim = bs_data.select_one('input[name="autim"]').attrs["value"]
            sid = bs_data.select_one('input[name="sid"]').attrs["value"]
            form_token = bs_data.select_one('input[name="form_token"]').attrs["value"]
            creation_time = bs_data.select_one('input[name="creation_time"]').attrs[
                "value"
            ]
            login = {
                "redirect": [
                    item.attrs["value"]
                    for item in bs_data.select('input[name="redirect"]')
                ],
                "creation_time": creation_time,
                "form_token": form_token,
                "sid": sid,
                "login": "登录",
                "autim": autim,
            }
            login_url = urljoin(resp.url, bs_data.select_one("#login").attrs["action"])
            reg_url = urljoin(resp.url, bs_data.select_one("a.button2").attrs["href"])
            return autim, sid, login, login_url, reg_url
        except Exception as e:
            error(f"[Parser->get_login_and_reg_payload]: {e}")
            raise e

    @staticmethod
    def get_sid(resp, default):
        try:
            sid = re.findall('sid=(.*?)"', resp.text)
            if sid:
                info(f"sid: {sid[0]}")
                return sid[0]
            else:
                return default
        except Exception as e:
            error(f"[Parser->get_sid]: {e}")
            return default

    @staticmethod
    def get_token_and_creation_time(resp):
        try:
            bs_data = bs_4(resp.text, "lxml")
            token = bs_data.select_one('input[name="form_token"]').attrs["value"]
            info(f"token: {token}")
            creation_time = bs_data.select_one('input[name="creation_time"]').attrs[
                "value"
            ]
            info(f"creation_time: {creation_time}")
            return token, creation_time
        except Exception as e:
            error(f"[Parser->get_token_and_creation_time]: {e}")
            return (None, None)

    @staticmethod
    def get_qa_answer_and_id(resp):
        try:
            qa_answer = re.findall("请在右边框中输入： (.*?)：</label>", resp.text)[0]
            info(f"qa_answer: {qa_answer}")
            bs_data = bs_4(resp.text, "lxml")
            qa_confirm_id = bs_data.select_one("#qa_confirm_id").attrs["value"]
            info(f"qa_confirm_id: {qa_confirm_id}")
            return qa_answer, qa_confirm_id
        except Exception as e:
            error(f"[Parser->get_qa_answer_and_id]: {e}")
            return (None, None)

    @staticmethod
    def get_captcha(func, resp):
        try:
            bs_data = bs_4(resp.text, "lxml")
            path = bs_data.select_one(".captcha>img").attrs["src"]
            confirm_id = re.findall("confirm_id=(.*?)&", path)[0]
            img_url = urljoin(resp.url, path)
            img_raw = func(img_url)
            if platform.system().upper() == "DARWIN":
                imgcat(img_raw)
            code = pytesseract.image_to_string(
                Image.open(BytesIO(img_raw)), lang="snum"
            ).replace(" ", "")
            info(f"captcha_code: {code}, confirm_id:{confirm_id}")
            # assert False
            return code, confirm_id
            # return input('code:'),confirm_id
        except Exception as e:
            error(f"[Parser->get_captcha]: {e}")
            return "TRBGR", "7c3601cd570d2650a89fd33b3b5238d1"

    @staticmethod
    def get_current_type(resp):
        try:
            types = {
                item.select_one(".index_list_title")
                .attrs["href"]
                .split("=")[1]
                .split("&")[0]: item.select_one("tr:nth-child(1) > td")
                .text.split()[0]
                .replace("查看更多", "")
                for item in bs_4(resp.text, "lxml").select(".ad_table_b")
            }
            info(types)
            return types
        except Exception as e:
            error(f"[Parser->get_current_type]: {e}")
            return {}

    @staticmethod
    def get_uid_and_sid(bs_data):
        try:
            uid = fix_nums(
                bs_data.select_one(
                    ".v_table_2 > tr:nth-child(5) > td:nth-child(2)"
                ).text
            )
            debug(f"uid: {uid}")
            sid = fix_nums(bs_data.select_one("tr:nth-child(3) > td:nth-child(2)").text)
            debug(f"sid: {sid}")
            return uid, sid
        except Exception as e:
            error(f"[Parser->get_uid_and_sid]: {e}")
            return (None, None)

    @staticmethod
    def get_person_data(bs_data):
        try:
            personDatas = {
                "salenums": fix_nums(
                    bs_data.select_one(
                        ".v_table_2 tr:nth-child(3) > td:nth-child(4)"
                    ).text
                ),
                "totalsales": float_format(
                    bs_data.select_one(
                        ".v_table_2 tr:nth-child(5) > td:nth-child(4)"
                    ).text
                ),
                "totalbuys": float_format(
                    bs_data.select_one(
                        ".v_table_2 tr:nth-child(7) > td:nth-child(4)"
                    ).text
                ),
            }
            username = bs_data.select_one(
                ".v_table_2 tr:nth-child(3) > td:nth-child(2)"
            ).text
            debug(f"personDatas: {personDatas}")
            debug(f"username: {username}")
            return personDatas, username
        except Exception as e:
            error(f"[Parser->get_person_data]: {e}")
            return {"salenums": 0, "totalsales": 0, "totalbuys": 0}, ""

    @staticmethod
    def get_reg_date(bs_data, default):
        try:
            reg_date_str = bs_data.select_one(
                ".v_table_2 tr:nth-child(7) > td:nth-child(2)"
            ).text
            debug(f"reg_date_str:{reg_date_str}")
            return moment.date(reg_date_str).format("YYYY-MM-DD")
        except Exception as e:
            error(f"[Parser->get_reg_date]: {e}")
            return default

    @staticmethod
    def get_detail_content(bs_data):
        try:
            content = " ".join(bs_data.select_one(".postbody .content").text.split())
            debug(f"content: {content}")
            return content
        except Exception as e:
            error(f"[Parser->get_detail_content]: {e}")
            return ""

    @staticmethod
    def get_img_urls(bs_data):
        try:
            urls = [_.attrs["src"] for _ in bs_data.select(".postbody img")]
            debug(urls)
            return urls
        except Exception as e:
            error(f"[Parser->get_img_urls]: {e}")
            return []

    @staticmethod
    def get_up_time(bs_data, current_year):
        try:
            to_current_year_datetime = moment.date(
                f"{current_year} "
                + bs_data.select_one("tr:nth-child(3) > td:nth-child(6)").text
            )
            real_up_time_tree = bs_data.select_one(".author")
            real_up_time_tree.a.extract()
            real_up_time_tree.span.extract()

            real_up_time = moment.date(
                real_up_time_tree.text.replace("年", "")
                .replace("月", "")
                .replace("日", "")
            )
            real_up_time = (
                real_up_time if real_up_time._date else to_current_year_datetime
            )
            return debug(real_up_time)
        except Exception as e:
            error(f"[Parser->get_up_time]: {e}")
            return moment.now()

    @staticmethod
    def get_details(bs_data, current_year, real_up_time, muti):
        try:
            return debug(
                {
                    "lasttime": moment.date(
                        f"{current_year} "
                        + bs_data.select_one("tr:nth-child(7) > td:nth-child(6)").text
                    ).format("YYYY-MM-DD HH:mm:ss"),
                    "priceBTC": float_format(
                        bs_data.select_one(
                            "tr:nth-child(3) > td:nth-child(4) > span"
                        ).text
                    ),
                    "priceUSDT": float_format(
                        bs_data.select_one(
                            "tr:nth-child(5) > td:nth-child(4)"
                        ).text.split()[0]
                    ),
                    "lines": muti["lines"],
                    "uptime": real_up_time.format("YYYY-MM-DD HH:mm:ss"),
                    "hot": muti["hot"],
                    "types": bs_data.select_one(
                        "tr:nth-child(5) > td:nth-child(2)"
                    ).text,
                    "status": bs_data.select_one(
                        "tr:nth-child(7) > td:nth-child(2)"
                    ).text,
                    "oversell": fix_nums(
                        bs_data.select_one("tr:nth-child(9) > td:nth-child(2)").text,
                        to=99999,
                    ),
                    "sold": fix_nums(
                        bs_data.select_one("tr:nth-child(7) > td:nth-child(4)").text,
                        to=99999,
                    ),
                }
            )
        except Exception as e:
            error(f"[Parser->get_details]: {e}")
            raise e

    @staticmethod
    def get_types(resp):
        try:
            for item in bs_4(resp.text, "lxml").select("table.m_area_a tr"):
                detail_path = item.select_one("div.length_400>a.text_p_link")
                if detail_path:
                    yield debug((item, urljoin(resp.url, detail_path.attrs["href"])))
        except Exception as e:
            error(f"[Parser->get_types]: {e}")
            return []

    @staticmethod
    def get_type_datas(item):
        try:
            return debug(
                {
                    "lines": fix_nums(
                        item.select_one("td:nth-child(7)").text.replace("天", "")
                    ),
                    "hot": fix_nums(item.select_one("td:nth-child(8)").text),
                    "title": item.select_one("td:nth-child(5)").text,
                    "area": item.select_one("td:nth-child(3)").text,
                }
            )
        except Exception as e:
            error(f"[Parser->get_type_datas]: {e}")
            raise e

    @staticmethod
    def get_index(bs_item, default="*"):
        try:
            return bs_item.select("td")[0].text
        except Exception as e:
            error(f"[Parser->get_index]: {e}")
            return default

    @staticmethod
    def get_max_page(resp, just_update):
        try:
            info("Parsing Max Page")
            # bs_data = bs_4(resp.text, "lxml")
            # max_page_str = bs_data.select('.page_b1')[-1].text
            max_page = (
                # fix_nums(max_page_str, error=1)
                30
                if not just_update
                else 1
            )
            info(f"MaxPage: {max_page}")
            return max_page
        except Exception as e:
            error(f"[Parser->get_max_page]: {e}")
            return 1
