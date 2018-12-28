import json
import time
from base64 import b64encode
from pprint import pprint
from urllib.parse import urljoin

import requests
import telepot
from celery import Celery
from peewee import fn
from retry import retry

from conf import Config
from model import DarkNet_DataSale, DarkNet_IMGS, DarkNet_Notice, DarkNet_User

telepot.api.set_proxy(Config.telegram_proxy)
bot = telepot.Bot(Config.telegram_token)
app = Celery(
    'darknet', broker=f'redis://{Config.redis_host}:{Config.redis_port}//')



@app.task()
def telegram(msg, sid,rid):
    bot.sendMessage(rid, msg)
    query = DarkNet_Notice.update({
        'telegram': True
    }).where(DarkNet_Notice.sid == sid)
    query.execute()


@app.task()
def telegram_withpic(pic,details,sid,rid):
    bot.sendPhoto(rid,pic,details)
    query = DarkNet_Notice.update({
          'telegram': True
     }).where(DarkNet_Notice.sid == sid)
    query.execute()

@app.task()
def logreport(msg):
    bot.sendMessage(Config.ReportGroupID,msg)

