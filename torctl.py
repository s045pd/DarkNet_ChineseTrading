import logging
import time

import requests
from pyquery import PyQuery as jq
from stem import Signal
from stem.control import Controller

logging.basicConfig(
    format="[%(asctime)s] >>> %(levelname)s  %(name)s: %(message)s", level=logging.INFO
)
loger = logging.getLogger("Torctl")
controller = Controller.from_port(port=9151)
controller.authenticate()


def main():

    while True:
        loger.info("NewID")
        checkIP()
        controller.signal(Signal.NEWNYM)
        time.sleep(60 * 10)


def checkIP():
    try:
        resp = requests.get(
            "https://ipinfo.info/html/my_ip_address.php",
            proxies={"https": "socks5://127.0.0.1:9150"},
        )
        loger.info(jq(resp.text)("#Text10 > p > span > b").text())
    except Exception as e:
        loger.error(e)


if __name__ == "__main__":
    main()
