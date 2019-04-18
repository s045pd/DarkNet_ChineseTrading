import logging
from termcolor import colored

logging.basicConfig(format="[%(asctime)s]%(message)s", level=logging.INFO)
Loger = logging.getLogger("ChineseTradingNetwork")


def info(txt):
    return Loger.info(f"{colored(txt, 'blue')}")


def success(txt):
    return Loger.info(f"{colored(txt, 'green')}")


def warning(txt):
    return Loger.info(f"{colored(txt, 'yellow')}")


def error(txt):
    return Loger.info(f"{colored(txt, 'red')}")
