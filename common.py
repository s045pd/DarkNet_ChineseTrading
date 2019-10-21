import datetime
import os
import random
import string
import time

import requests
from faker import Faker
from PIL import Image
from pypinyin import Style, lazy_pinyin, pinyin
from stem import Signal
from stem.control import Controller

import _io
from log import error, info, success, warning

faker_langs = ["zh_CN", "zh_TW"]


def error_log(target="", default=None, raise_err=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error(f"[{target} {func.__name__}]: {e}")
                if raise_err:
                    raise e
                return default

        return wrapper

    return decorator


@error_log()
def make_new_tor_id():
    info("reload tor")
    try:
        controller = Controller.from_port(port=9151)
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        resp = requests.get(
            "http://icanhazip.com/", proxies={"https": "socks5://127.0.0.1:9150"}
        )
        success(f"current ip: {resp.text.strip()}")
    except Exception as e:
        raise
    finally:
        controller.close()


@error_log()
def init_path(root):
    if not os.path.exists(root):
        os.makedirs(root)


@error_log()
def random_key(length=20):
    return "".join(
        (
            random.choice(
                random.choice(
                    (
                        string.ascii_uppercase,
                        string.ascii_lowercase,
                        "".join(map(str, range(0, 9))),
                    )
                )
            )
            for i in range(1, length)
        )
    )


@error_log()
def fake_datas():
    target = Faker(random.choice(faker_langs))
    names = list(
        map(random.choice, pinyin(target.name(), style=Style.TONE2, heteronym=True))
    )
    names.append(random_key(5))
    return "".join(names)


@error_log()
def fix_nums(data, to=9_999_999, error=-1):
    """
        专治超量
    """
    try:
        nums = int(data)
        return nums if nums < to else to
    except Exception as e:
        return error


@error_log()
def float_format(data):
    try:
        return float(data)
    except Exception as e:
        return 0.0


def time_delay(seconds=120):
    """
        生效期，防止刚注册的账户被ban
    """
    return datetime.datetime.now() + datetime.timedelta(seconds=seconds)


def read_exif_gps(file: _io.BytesIO):
    def format(datas):
        return (
            datas[0][0]
            + (datas[1][0] // datas[1][1]) / 60
            + (datas[1][0] % datas[1][1]) / 3600
        )

    gps_key = 34853
    gps_data = Image.open(file).getexif().get(gps_key, None)
    if gps_data:
        return (
            (1 if gps_data[3] == "E" else -1) * format(gps_data[4]),
            (1 if gps_data[1] == "N" else -1) * format(gps_data[2]),
        )
