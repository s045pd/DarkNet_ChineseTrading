import platform
from io import BytesIO

import pytesseract
from imgcat import imgcat
from PIL import Image

from common import convert_num, error_log
from conf import Config
from log import *


class Parser:
    @staticmethod
    @error_log()
    def predict_captcha(func, path="/entrance/code76.php"):
        """
            验证码识别在这里
        """
        raw = func(path).content
        if platform.system().upper() == "DARWIN":
            imgcat(raw)
        # img = two_value(Image.open(BytesIO(raw), mode="r"))
        img = Image.open(BytesIO(raw))
        # code = self.predicter.rec_image(img)
        # warning(f"predict: {code}")
        code = pytesseract.image_to_string(img, lang="snum").replace(" ", "")
        warning(f"pytesseract: {code}")
        return input("code:").strip()
        return code

    @staticmethod
    @error_log()
    def parse_summary(resp):
        try:
            trs = resp.html.find("table.u_ea_a > tr")[3:-1][::2]
            for tr in trs:
                href = tr.pq("td:nth-child(6) a").attr["href"]
                yield debug(
                    (
                        href,
                        {
                            "sid": href.split("=")[-1],
                            "uptime": tr.pq("td:nth-child(2)").text(),
                            "user": tr.pq("td:nth-child(3)").text(),
                            "title": tr.pq("td:nth-child(4)").text(),
                            "priceBTC": convert_num(
                                tr.pq("td:nth-child(5)").text(), float
                            ),
                        },
                    )
                )

        except Exception as e:
            raise e
            return []

    @staticmethod
    @error_log()
    def parse_details(resp, img_func, types):
        T = resp.html.pq(".v_table_1")
        try:
            return (
                {
                    "priceUSDT": convert_num(
                        T("tr:nth-child(3) >  td:nth-child(4) > span").text(), float
                    ),
                    "status": resp.html.search("<td>交易状态:</td><td>{}</td>")[0],
                    "sold": resp.html.search("<td>本单成交:</td><td>{}</td>")[0],
                    "area": types,
                    "link": resp.url,
                    "lasttime": T(
                        ".v_table_1 > tr:nth-child(5) > td:nth-child(6)"
                    ).text(),
                    "text": resp.html.pq(".div_masterbox > t").text(),
                },
                {
                    "img": [
                        img_func(img.get("src"))
                        for img in resp.html.pq(".attachbox > img")
                    ]
                },
            )
        except Exception:
            # breakpoint()
            raise e

    @staticmethod
    @error_log()
    def parse_max_page(resp, just_update=True):
        page = 1
        try:
            page = (
                convert_num(resp.html.pq(".button_page")[-1].text.strip(), int)
                if not just_update
                else 1
            )
        except Exception as e:
            pass
        finally:
            info(f"max {page=}")
            return page
