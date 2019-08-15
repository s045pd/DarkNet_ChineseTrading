import json
import time
from base64 import b64encode
from pprint import pprint
from urllib.parse import urljoin
from log import success, error
import copy

import requests
import telepot
from celery import Celery
from celery.schedules import crontab
from peewee import fn
from retry import retry

from conf import Config
from model import DarkNet_DataSale, DarkNet_IMGS, DarkNet_Notice, DarkNet_User
from common import read_exif_gps
from io import BytesIO

telepot.api.set_proxy(Config.telegram_proxy)
bot = telepot.Bot(Config.telegram_token)
app = Celery("darknet", broker=f"redis://{Config.redis_host}:{Config.redis_port}//")


@app.task()
def telegram(msg, sid, rid):
    bot.sendMessage(rid, msg)
    query = DarkNet_Notice.update({"telegram": True}).where(DarkNet_Notice.sid == sid)
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
            rid, target, details + (f"\nEXIF GPS: {gps_data}" if gps_data else "")
        )
        if gps_data:
            bot.sendLocation(rid, *gps_data[::-1])
        query = DarkNet_Notice.update({"telegram": True}).where(
            DarkNet_Notice.sid == sid
        )
        query.execute()
    except Exception as e:
        error(f"telegram_with_pic: {e}")


@app.task()
def logreport(msg):
    bot.sendMessage(Config.ReportGroupID, msg)


@app.task()
def keep_alive():
    pass


@app.task()
def auto_reg():
    pass


# app.conf.update(
#     timezone='Asia/Shanghai',
#     enable_utc=True,
#     beat_schedule={
#         'auto_reg_task':{
#             'task'
#         }
#     })
