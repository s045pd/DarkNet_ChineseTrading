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
from selenium import webdriver

from conf import Config
from model import DarkNet_DataSale, DarkNet_IMGS, DarkNet_Notice, DarkNet_User


def CreateChromeSession(proxy_url, headless=True):
    options = webdriver.ChromeOptions()
    if proxy_url:
        options.add_argument(
            f'--proxy-server={proxy_url.replace("socks5h","socks5")}')
    if headless:
        options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options)
    driver.set_page_load_timeout(30)

    # user = DarkNet_User.select().where(DarkNet_User.useful == True).limit(1)
    # driver.find_element_by_id('username').send_keys(user[0].user)  # 要登录的用户名
    # driver.find_element_by_id('password').send_keys(user[0].pwd)  # 对应的密码
    # driver.find_element_by_name("login").click()
    # driver.implicitly_wait(30)
    return driver


def CreatePhantomjsSession(proxy_url):
    """ 创建一个phantomjs的session
        proxy: tor代理地址
    """
    proxy_args = [
        f'--proxy={proxy_url.split("socks5h://")[1]}',
        '--proxy-type=socks5',
    ]
    driver = webdriver.PhantomJS(service_args=proxy_args)
    driver.set_page_load_timeout(30)
    return driver


telepot.api.set_proxy(Config.telegram_proxy)
bot = telepot.Bot(Config.telegram_token)
Rooms = bot.getUpdates()
app = Celery(
    'darknet', broker=f'redis://{Config.redis_host}:{Config.redis_port}//')


ToendJS = """
        (function () {
            var y = 0;
            var step = 100;
            window.scroll(0, 0);

            function f() {
                if (y < document.body.scrollHeight) {
                    y += step;
                    window.scroll(0, y);
                    setTimeout(f, 100);
                } else {
                    window.scroll(0, 0);
                    document.title += "scroll-done";
                }
            }

            setTimeout(f, 1000);
        })();
    """  # 模拟下拉js


@app.task()
def telegram(channelname, msg, sid):
    for item in Rooms:
        roomchat = item['channel_post']['chat']
        if channelname == roomchat['title'] and DarkNet_Notice.select().where(DarkNet_Notice.sid == sid):
            rid = roomchat['id']
            bot.sendMessage(rid, msg)
            query = DarkNet_Notice.update({
                'telegram': True
            }).where(DarkNet_Notice.sid == sid)
            query.execute()


@app.task()
def UpdateImages(cookie, header, proxy, sid):
    for img in DarkNet_IMGS.select().where((DarkNet_IMGS.sid == sid) & (DarkNet_IMGS.islink == True)):
        imgres = json.dumps([GetPicBase64(cookie, header, proxy, link)
                             for link in json.loads(img.img) if 'http' in link])
        pprint(imgres)
        query = DarkNet_IMGS.update({
            "img": imgres,
            "islink": False
        }).where(DarkNet_IMGS.sid == sid)
        query.execute()


def GetPicBase64(cookie, header, proxy, link):
    return bytes.decode(b64encode(requests.get(link, headers=header, cookies=cookie, proxies=proxy).content))
