import pathlib
import random
import string
import time
import re

import requests
from PIL import Image
from stem import Signal
from stem.control import Controller

import _io
from .default import Config
from .log import *


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
def convert_num(data, types=str):
    data = data.strip()
    if not (reg_res := re.search("[0-9]+(\.[0-9]*)?", data)):
        return "0"
    else:
        if types is float:
            return float(data)
        elif types is int:
            return int(float(data))
        else:
            return types(data)
    return "0"


@error_log()
def make_new_tor_id(port: int = 9051, ip_link="http://icanhazip.com/") -> None or str:
    info("reload tor")
    try:
        controller = Controller.from_port(port=port)
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        resp = requests.get(ip_link, proxies={"http": Config.tor_proxy})
        ip = resp.text.strip()
        success(f"{ip=}")
        return ip
    except Exception as e:
        raise
    finally:
        time.sleep(2)
        # controller.close()


@error_log()
def init_path(root: str) -> pathlib.Path:
    return pathlib.Path(root).mkdir(exists=True)


@error_log()
def random_key(length: int = 20) -> str:
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
            for i in range(1, length + 1)
        )
    )


@error_log()
def read_exif_gps(file: _io.BytesIO):
    def format(datas):
        return datas[0][0] + (datas[1][0] // datas[1][1]) / 60 + (datas[1][0] % datas[1][1]) / 3600

    gps_key = 34853
    gps_data = Image.open(file).getexif().get(gps_key, None)
    if gps_data:
        return (
            (1 if gps_data[3] == "E" else -1) * format(gps_data[4]),
            (1 if gps_data[1] == "N" else -1) * format(gps_data[2]),
        )


@error_log()
def send_mail():
    pass


@error_log()
def recv_mail():
    pass


@error_log()
def get_captcha_code_by_mail():
    pass
