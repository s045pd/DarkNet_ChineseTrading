import pathlib
import random
import string
import time

import requests
from PIL import Image
from stem import Signal
from stem.control import Controller

import _io
from conf import Config
from log import *


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
    if types in {float, int}:
        try:
            return types(data)
        except Exception as e:
            return types(0)


@error_log()
def make_new_tor_id():
    info("reload tor")
    try:
        controller = Controller.from_port(port=9151)
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        resp = requests.get("http://icanhazip.com/", proxies={"http": Config.tor_proxy})
        ip = resp.text.strip()
        success(f"{ip=}")
    except Exception as e:
        raise
    finally:
        time.sleep(2)
        controller.close()


@error_log()
def init_path(root):
    pathlib.Path(root).mkdir(exists=True)


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
