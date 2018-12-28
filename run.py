
import json
import logging
import math
import os
import random
import re
import string
import sys
import time
from base64 import b64encode
from urllib.parse import urljoin

# import pudb;pu.db
import moment
import progressbar
import pymysql
import requests
from peewee import fn
from pyquery import PyQuery as jq
from retry import retry
from termcolor import colored
from io import BytesIO
from conf import Config
from model import (DarkNet_DataSale, DarkNet_IMGS, DarkNet_Notice,
                   DarkNet_Saler, DarkNet_User, DarkNetWebSites)
from task import telegram,logreport,telegram_withpic


TYPES = 'ChineseTradingNetwork'
logging.basicConfig(
    format="[%(asctime)s] >>> %(levelname)s  %(name)s: %(message)s", level=logging.INFO)

DefaultLIST = [
    ('deepmix3m7iv2vcz.onion', False),
    ('deepmix2j3cv4bds.onion', False),
    ('deepmix2z2ayzi46.onion', False),
    ('deepmix7j72q7kvz.onion', False),
    ('bmp3qqimv55xdznb.onion', True),
]


def FixNums(data, to=9999999, error=-1):
    """
        专治超量
    """
    try:
        nums = int(data)
        return nums if nums < to else to
    except Exception as e:
        return error


class DarkNet_ChineseTradingNetwork(object):

    def __init__(self):
        self.loger = logging.getLogger(f'DarkNet_{TYPES}')

        self.info = lambda txt: self.loger.info(colored(txt, 'blue'))
        self.report = lambda txt: self.loger.info(colored(txt, 'green'))
        self.warn = lambda txt: self.loger.info(colored(txt, 'yellow'))
        self.error = lambda txt: self.loger.info(colored(txt, 'red'))
        self.session = requests.Session()
        self.session.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Referer": "http://bmp3qqimv55xdznb.onion/index.php",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
        }
        self.proxy_url = 'socks5h://127.0.0.1:9150'
        self.session.proxies = {
            'https': self.proxy_url,
            'http': self.proxy_url
        }
        self.usemaster = True
        self.master = None
        self.sid = ''
        self.justupdate = False

        self.noticerange = 0
        self.rootpath = 'datas'
        self.screenpath = 'screen_shot'
        list(map(self.InitPath, [self.rootpath, self.screenpath]))

    def InitAdd(self, domainLIST):
        for item in domainLIST:
            if not DarkNetWebSites.select().where(DarkNetWebSites.domain == item[0]):
                Model = DarkNetWebSites()
                Model.domain = item[0]
                Model.ismaster = item[1]
                Model.alive = True
                Model.target = TYPES
                Model.save()

    @retry()
    def FirstFetch(self):
        targets = DarkNetWebSites.select().where(
            DarkNetWebSites.ismaster == self.usemaster)
        if not targets:
            return
        target = targets[0]
        try:
            self.warn(f'[{target.domain}]Getting PHPSESSID')
            resp = self.session.get(f'http://{target.domain}')
            target.ismaster = True
            target.title = jq(resp.text)('title').text()
            self.usemaster = True
            self.master = target
            self.domain = target.domain
            user = DarkNet_User.select().where(DarkNet_User.useful ==
                                               True).order_by(fn.Rand()).limit(1)
            if not bool(user):
                self.Reg()
            else:
                self.usr = user[0].user
                self.pwd = user[0].pwd
                if random.choice([1, 0]):  # 佛系注册堆积账号池
                    self.Reg()
            return True
        except KeyboardInterrupt:
            pass
        except requests.Timeout:
            target.alive = False
            target.ismaster = False
            self.usemaster = False
        except Exception as e:
            raise
        finally:
            target.save()

    @retry(delay=2,tries=20)
    def Reg(self):
        self.warn('Start Regging')
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",

            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": f"http://{self.domain}",
            "Pragma": "no-cache",
            "Referer": f"http://{self.domain}/ucp.php?mode=register&sid={self.sid}",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
        }
        step1resp = self.session.get(
            f"http://{self.domain}/ucp.php?mode=register").text
        step1 = jq(step1resp)
        self.sid = re.findall('sid=(.*?)"', step1resp)[0]
        token = step1('input[name="form_token"]').attr('value')
        creation_time = step1('input[name="creation_time"]').attr('value')
        self.info(f"Get Token: {token} Create_time: {creation_time}")
        url = f"http://{self.domain}/ucp.php?mode=register&sid={self.sid}"
        step2resp = self.session.post(url, data={
            "agreed": "===好的,我已明白,请跳转到下一页继续注册====",
            "change_lang": "",
            "creation_time": creation_time,
            "form_token": token
        }, headers=headers)

        self.SaveError('step2.html', step2resp)
        step2 = jq(step2resp.text)
        token = step2('input[name="form_token"]').attr('value')
        creation_time = step2('input[name="creation_time"]').attr('value')
        qa_answer = re.findall('请在右边框中输入： (.*?)：</label>',step2resp.text)[0]
        self.report(f'Got answer: {qa_answer}')
        qa_confirm_id = step2('#qa_confirm_id').attr('value') 

        self.usr = self.RandomKey()
        self.pwd = self.RandomKey()
        self.info(f'set Usr: {self.usr} ,Pwd: {self.pwd}')
        data = {
            "username": self.usr,
            "new_password": self.pwd,
            "password_confirm": self.pwd,
            "email": "xxxx@xxxx.xxx",
            "lang": "zh_cmn_hans",
            "tz_date": "UTC+08:00+-+Asia/Brunei+-+" + moment.now().format("DD+MM月+YYYY,+HH:mm"),
            "tz": "Asia/Hong_Kong",
            "agreed": "true",
            "change_lang": "0",
            "qa_answer":qa_answer,
            "qa_confirm_id":qa_confirm_id,
            "submit": " 用户名与密码已填好,+点此提交 ",
            "creation_time": creation_time,
            "form_token": token
        }
        resp = self.session.post(url, data=data, headers=headers)
        try:
            assert '感谢注册' in resp.text
            self.report('Reg success！')
            DarkNet_User.create(**{
                'user': self.usr,
                'pwd': self.pwd
            })
        except AssertionError:
            self.error(jq(resp.text).text())
            self.SaveError('reg.html', resp)

    @retry(delay=2,tries=20)
    def Login(self):
        """
            ### 再次尝试
            1.因为网络问题重试

            ### 重新注册
            2.因为账户被封重试
            3.因为账户认证错误重试
        """
        self.warn('Login...')
        url = f'http://{self.domain}/ucp.php?mode=login'
        data = {
            "username": self.usr,
            "password": self.pwd,
            "login": "登录",
            "redirect": f"./index.php&sid={self.sid}"
        }
        resp = self.session.post(url, data=data, verify=False, timeout=120)
        self.sid = ''.join(re.findall("sid=(.*?)'", resp.text)[:1])
        self.info(f"SID: {self.sid}")
        if self.usr not in resp.text:
            self.error('Auth faild')
            self.SaveError('Autherror.html', resp)
            if "已被封禁" in resp.text:
                DarkNet_User.update({
                    "useful": False
                }).where(DarkNet_User.user == self.usr).execute()
            self.Reg()
            raise ValueError
        else:
            self.report('Auth Success')
            self.types = {item('.index_list_title').attr('href').split('=')[1].split('&')[0]: item('tr:nth-child(1) > td').text(
            ).split()[0] for item in jq(resp.text)('.ad_table_b').items()}
            self.report(self.types)

    def SaveError(self, filename, resp):
        fullfilepath = f"{self.rootpath}/{filename}"
        self.error(f"Html Log Saved to {fullfilepath}")
        with open(fullfilepath, 'w') as f:
            f.write(resp.text)

    @retry()
    def GetTypeDatas(self, qeaid, name, page=1):
        url = f"http://{self.domain}/pay/user_area.php?page_y1={page}&q_u_id=0&m_order=&q_ea_id={qeaid}&sid={self.sid}#page_y1"
        self.warn(url)
        resp = self.session.get(url)
        resp.encoding = "utf8"
        hasres = False
        try:
            self.CheckIfNeedLogin(resp)
            self.SaveError(f'{qeaid}_{name}_{page}.html', resp)
            self.info(len(resp.text))
            jqdata = jq(resp.text)
            for item in jqdata('table.m_area_a tr').items():
                detailPath = item('div.length_400>a').attr('href')
                if detailPath:
                    detailsURL = urljoin(resp.url, detailPath)
                    self.GetDetails(detailsURL, {
                        'lines':  FixNums(item('td:nth-child(7)').text().replace('天', '')),
                        'hot': FixNums(item('td:nth-child(8)').text()),
                        'title': item('td:nth-child(5)').text(),
                        'area': item('td:nth-child(3)').text()
                    })
                    hasres = True
            if page == 1:
                maxpageStr = ''.join(
                    jqdata('.page_b1:nth-last-child(1)').text().split())
                return FixNums(maxpageStr, to=1, error=1) if maxpageStr and not self.justupdate else 1
            if hasres:
                return True
        except Exception as e:
            self.error(f"GetTypeDatas: {e}")
            self.SaveError('GetTypeDatas.html', resp)
            raise

    def CheckIfNeedLogin(self, resp, passed=False, needraise=True):
        if passed or "缓存已经过期" in resp.text:
            """
                登录超时重新登录
            """
            if self.FirstFetch():
                self.Login()
        elif "您必须注册并登录才能浏览这个版面" in resp.text:
            """
                账户遭到封锁重新注册
            """
            self.Reg()

        elif "您的回答不正确" in resp.text:
            time.sleep(20)
            self.Reg()

    def NewNet(self):
        pass

    # @retry((requests.exceptions.ConnectionError, ValueError))
    @retry((requests.exceptions.ConnectionError))
    def GetDetails(self, url, muti):
        resp = self.session.get(url)
        resp.encoding = "utf8"
        self.CheckIfNeedLogin(resp)
        jqdata = jq(resp.text)
        jqdetail = jqdata('.v_table_1')
        jqperson = jqdata('.v_table_2')

        try:
            uid = FixNums(jqperson('tr:nth-child(5) > td:nth-child(2)').text())
            sid = FixNums(jqdetail(
                'tr:nth-child(3) > td:nth-child(2)').text())

            details = DarkNet_DataSale.select().where((DarkNet_DataSale.sid == sid))
            person = DarkNet_Saler.select().where((DarkNet_Saler.uid == uid))
            notice = DarkNet_Notice.select().where((DarkNet_Notice.sid == sid))
            img = DarkNet_IMGS.select().where((DarkNet_IMGS.sid == sid))

            personDatas = {
                "salenums": FixNums(jqperson('tr:nth-child(3) > td:nth-child(4)').text()),
                "totalsales": float(jqperson('tr:nth-child(5) > td:nth-child(4)').text()),
                "totalbuys": float(jqperson('tr:nth-child(7) > td:nth-child(4)').text())
            }
            if not person:
                personDatas.update({
                    "uid": uid,
                    "user": jqperson('tr:nth-child(3) > td:nth-child(2)').text(),
                    "regtime": moment.date(jqperson('tr:nth-child(7) > td:nth-child(2)').text()).format('YYYY-MM-DD'),
                })
                person = DarkNet_Saler.create(**personDatas)
            else:
                DarkNet_Saler.update(personDatas).where(
                    (DarkNet_Saler.uid == uid)).execute()
                person = person[0].uid

            if not notice:
                notice = DarkNet_Notice.create(**{"sid": sid})
            else:
                notice = notice[0].sid
            
            detailImages = None
            if not img:
                urls = [_.attr('src') for _ in jqdata('.postbody img').items()]
                img = DarkNet_IMGS.create(**{
                    "sid": sid,
                    "img": urls,
                    "detail": ' '.join(jqdata('.postbody .content').text().split()) 
                })
                detailImages = self.SavePics(urls, sid)
            else:
                img = img[0].sid

            currentYear = moment.now().year
            soldNum = FixNums(
                jqdetail('tr:nth-child(7) > td:nth-child(4)').text(), to=99999)
            toCurrentYearDateTime = moment.date(
                f"{currentYear} " + jqdetail('tr:nth-child(3) > td:nth-child(6)').text())
            RealUpTimeJQ = jqdata('.author')
            RealUpTimeJQ.remove('a')
            RealUpTimeJQ.remove('span')
            RealUpTime = moment.date(
                RealUpTimeJQ.text().replace('年', '').replace('月', '').replace('日', ''))
            RealUpTime = RealUpTime if RealUpTime._date else toCurrentYearDateTime
            detailsDatas = {
                "lasttime": moment.date(f"{currentYear} "+jqdetail('tr:nth-child(7) > td:nth-child(6)').text()).format('YYYY-MM-DD HH:mm:ss'),
                "priceBTC": float(jqdetail('tr:nth-child(3) > td:nth-child(4) > span').text()),
                "priceUSDT": float(jqdetail('tr:nth-child(5) > td:nth-child(4)').text().split()[0]),
                "lines": muti['lines'],
                "uptime": RealUpTime.format('YYYY-MM-DD HH:mm:ss'),
                "hot": muti['hot'],
                "types": jqdetail('tr:nth-child(5) > td:nth-child(2)').text(),
                "status": jqdetail('tr:nth-child(7) > td:nth-child(2)').text(),
                "oversell": jqdetail('tr:nth-child(9) > td:nth-child(2)').text(),
                "sold": soldNum
            }

            if not details:
                detailsDatas.update({
                    "sid": sid,
                    "user": person,
                    "area": muti['area'],
                    "title": muti['title'],
                    "detailurl": url,
                    "img": img,
                    "notice": notice
                })
                details = DarkNet_DataSale.create(**detailsDatas)
                self.MakeMsg(details,img.detail,detailImages, sid)
            else:
                self.warn(f'-{RealUpTime}- {muti["title"]}' )
                DarkNet_DataSale.update(detailsDatas).where(
                    (DarkNet_DataSale.sid == sid)).execute()

        except Exception as e:
            self.error(f"GetDetails {e}")
            self.SaveError("error_264.html", resp)
            raise


    def MakeMsg(self, details, content,imgs ,sid):
        msg = f'[{details.uptime}]\n{details.title}\n\nPrice:${details.priceUSDT}\n\n\n${content}'
        msg = msg if len(msg)<1000 else msg[:997] + '...'
        self.report(msg)
        if moment.date(details.uptime) > moment.now().replace(hours=0, minutes=0, seconds=0).add(days=self.noticerange):
            if not imgs:
                telegram.delay(msg, sid, Config.darknetchannelID)
            else:
                telegram_withpic(imgs[0],msg,sid,Config.darknetchannelID)

    @staticmethod
    def RandomKey(length=20):
        return ''.join((random.choice(random.choice((string.ascii_uppercase, string.ascii_lowercase, ''.join(map(str, range(0, 9)))))) for i in range(1,  length)))

    @staticmethod
    def InitPath(root):
        if not os.path.exists(root):
            os.makedirs(root)

    def GetPicBase64(self, link):
        return link if 'http' not in link else bytes.decode(b64encode(self.GetPic(link)))

    @retry()
    def GetPic(self, link):
        return self.session.get(link).content

    def SavePics(self, urls, sid):
        imageBox = []
        for index, url in enumerate(filter(lambda url: 'http' in url, urls)):
            with open(f'{self.screenpath}/{sid}_{index}.png', 'wb') as imgfile:
                singelPIC = self.GetPic(url)
                imgfile.write(singelPIC)
                imageBox.append(BytesIO(singelPIC))
        return imageBox

    def Run(self):
        self.InitAdd(DefaultLIST)
        while True:
            self.CheckIfNeedLogin(None, True, False)
            for qeaid, name in self.types.items():
                maxpage = self.GetTypeDatas(qeaid, name)
                self.info(f"MaxPage: {maxpage}")
                for page in range(1, maxpage):
                    if not self.GetTypeDatas(qeaid, name, page):
                        break


if __name__ == "__main__":
    while True:
        try:
            DarkNet_ChineseTradingNetwork().Run()
        except KeyboardInterrupt:
            break 
        except Exception as e:
            logreport.delay(str(e))
            time.sleep(10*60)
