import copy
import json
import time
from base64 import b64encode
from io import BytesIO
from pprint import pprint
from urllib.parse import urljoin

import requests
import telepot
from celery import Celery
from celery.schedules import crontab
from peewee import fn
from retry import retry

from common import read_exif_gps
from conf import Config
from log import error, success
from model import events

telepot.api.set_proxy(Config.tg_proxy)
bot = telepot.Bot(Config.tg_token)
app = Celery("darknet", broker=f"redis://{Config.redis_host}:{Config.redis_port}//")


@app.task()
def telegram(msg, sid, rid):
    bot.sendMessage(rid, msg)
    query = events.update({"notice": True}).where(events.sid == sid)
    query.execute()


@app.task()
def telegram_with_pic(pics, details, sid, rid):
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


@app.task()
def logreport(msg):
    bot.sendMessage(Config.tg_report_group_id, msg)
