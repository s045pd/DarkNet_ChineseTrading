import time
import requests
from pyquery import PyQuery as jq
from stem import Signal
from stem.control import Controller
from log import success, info, error, warning
import random
import string
import os


def make_new_tor_id():
    info("New Tor ID")
    controller = Controller.from_port(port=9151)
    controller.authenticate()
    controller.signal(Signal.NEWNYM)
    try:
        resp = requests.get(
            "https://ipinfo.info/html/my_ip_address.php",
            proxies={"https": "socks5://127.0.0.1:9150"},
        )
        success(f'Current IP: {jq(resp.text)("#Text10 > p > span > b").text()}')
    except Exception as e:
        error(e)


def init_path(root):
    if not os.path.exists(root):
        os.makedirs(root)


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


def fix_nums(data, to=9_999_999, error=-1):
    """
        专治超量
    """
    try:
        nums = int(data)
        return nums if nums < to else to
    except Exception as e:
        return error


def float_format(data):
    try:
        return float(data)
    except Exception as e:
        return 0.0
