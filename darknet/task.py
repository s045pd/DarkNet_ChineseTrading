import copy
from typing import List

import telepot

from .common import read_exif_gps
from .default import Config
from .log import error, success
from .model import events

telepot.api.set_proxy(Config.tg_proxy)
bot = telepot.Bot(Config.tg_token)


def telegram(msg: str, sid: str, rid: str) -> None:
    bot.sendMessage(rid, msg)
    query = events.update({"notice": True}).where(events.sid == sid)
    query.execute()


def telegram_with_pic(pics: List[str], details: str, sid: str, rid: str) -> None:
    try:
        target = pics[0]
        gps_data = None

        for pic in pics:
            try:
                gps_data = read_exif_gps(copy.deepcopy(pic))
                if gps_data:
                    success(f"find gps data: {gps_data}")
                    target = pic
                    break
            except Exception as e:
                error(e)
        bot.sendPhoto(
            rid,
            target.open("rb"),
            details + (f"\nEXIF GPS: {gps_data}" if gps_data else ""),
        )
        if gps_data:
            bot.sendLocation(rid, *gps_data[::-1])
        query = events.update({"notice": True}).where(events.sid == sid)
        query.execute()
    except Exception as e:
        error(f"telegram_with_pic: {e}")


def logreport(msg):
    bot.sendMessage(Config.tg_report_group_id, msg)
