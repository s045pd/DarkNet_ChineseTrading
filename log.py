import logging

from termcolor import colored

from conf import Config

logging.basicConfig(format="[%(asctime)s]%(message)s", level=logging.INFO)
Loger = logging.getLogger("ChineseTradingNetwork")


limit = (
    lambda _: (
        str(_)[: Config.max_log_len]
        + ("..." if len(str(_)) > Config.max_log_len else "")
    )
    if Config.limit_log
    else _
)


def info(txt):
    Loger.info(f"{colored(limit(txt), 'blue')}")
    return txt


def success(txt):
    Loger.info(f"{colored(limit(txt), 'green')}")
    return txt


def warning(txt):
    Loger.info(f"{colored(limit(txt), 'yellow')}")
    return txt


def error(txt):
    Loger.info(f"{colored(limit(txt), 'red')}")
    return txt


def debug(txt):
    if Config.debug:
        Loger.info(f"{colored(limit(txt),'cyan')}")
    return txt
