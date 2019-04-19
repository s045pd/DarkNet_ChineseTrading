import logging
from termcolor import colored
from conf import Config

logging.basicConfig(format="[%(asctime)s]%(message)s", level=logging.INFO)
Loger = logging.getLogger("ChineseTradingNetwork")


def info(txt):
    Loger.info(f"{colored(txt, 'blue')}")
    return txt


def success(txt):
    Loger.info(f"{colored(txt, 'green')}")
    return txt


def warning(txt):
    Loger.info(f"{colored(txt, 'yellow')}")
    return txt


def error(txt):
    Loger.info(f"{colored(txt, 'red')}")
    return txt


def debug(txt):
    if Config.debug:
        Loger.info(f"{colored(txt,'cyan')}")
    return txt
