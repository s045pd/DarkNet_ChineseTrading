import datetime
import hashlib
import json

import pymysql
from peewee import *

from conf import Config
from peewee import __exception_wrapper__

Links = {
    "host": Config.mysql_host,
    "port": Config.mysql_port,
    "user": Config.mysql_usr,
    "password": Config.mysql_pass,
}

try:
    con = pymysql.connect(**Links)
    with con.cursor() as cursor:
        cursor.execute(
            f"create database {Config.mysql_db} character set UTF8mb4 collate utf8mb4_bin"
        )
    con.close()
except pymysql.err.ProgrammingError as e:
    if "1007" in str(e):
        pass
except Exception as e:
    raise e


class RetryOperationalError(object):
    def execute_sql(self, sql, params=None, commit=True):
        try:
            cursor = super(RetryOperationalError, self).execute_sql(sql, params, commit)
        except OperationalError:
            if not self.is_closed():
                self.close()
            with __exception_wrapper__:
                cursor = self.cursor()
                cursor.execute(sql, params or ())
                if commit and not self.in_transaction():
                    self.commit()
        return cursor


class RetryMySQLDatabase(RetryOperationalError, MySQLDatabase):
    pass


Links["database"] = Config.mysql_db
db = RetryMySQLDatabase(**Links, charset="utf8mb4")


class DarkNet_Domain(Model):
    mid = AutoField(primary_key=True)
    domain = CharField(max_length=180)
    datetime = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


class DarkNet_Saler(Model):
    uid = IntegerField(primary_key=True, verbose_name="用户编号")
    user = CharField(unique=True, max_length=20, verbose_name="用户外键")
    regtime = DateField(verbose_name="注册时间")
    salenums = IntegerField(verbose_name="在售单数")
    totalsales = FloatField(verbose_name="总出售额")
    totalbuys = FloatField(verbose_name="总购买额")

    class Meta:
        database = db


class DarkNet_User(Model):
    user = CharField(max_length=20, primary_key=True, verbose_name="用户名")
    pwd = CharField(max_length=20, verbose_name="密码")
    useful = BooleanField(default=True)
    intime = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


class DarkNet_IMGS(Model):
    sid = IntegerField(primary_key=True, verbose_name="交易编号")
    img = TextField(verbose_name="图片json")
    detail = TextField(default=json.dumps([]), verbose_name="备注")
    islink = BooleanField(default=True)

    class Meta:
        database = db


class DarkNet_Notice(Model):
    sid = IntegerField(primary_key=True, verbose_name="交易编号")
    wechat = BooleanField(default=False, verbose_name="企业微信")
    email = BooleanField(default=False, verbose_name="邮件")
    telegram = BooleanField(default=False, verbose_name="telegram")

    class Meta:
        database = db


class DarkNet_DataSale(Model):
    sid = IntegerField(primary_key=True, verbose_name="交易编号")

    intime = DateTimeField(default=datetime.datetime.now, verbose_name="数据插入时间")
    uptime = DateTimeField(verbose_name="发布时间")
    lasttime = DateTimeField(verbose_name="商家最后在线")
    user = ForeignKeyField(DarkNet_Saler, on_delete=None, verbose_name="发布用户ID")
    area = CharField(max_length=32, verbose_name="区域")
    title = CharField(max_length=155, verbose_name="发布标题")
    priceBTC = FloatField(verbose_name="出售价格（BTC）")
    priceUSDT = FloatField(verbose_name="出售价格（美元）")
    lines = IntegerField(verbose_name="保护期")
    hot = IntegerField(verbose_name="关注度")
    detailurl = CharField(max_length=255, verbose_name="详情地址")

    types = CharField(max_length=32, verbose_name="交易类型")
    status = CharField(max_length=32, verbose_name="交易状态")
    oversell = BigIntegerField(verbose_name="出售数量（出售数量）")  # 出售数量
    sold = IntegerField(verbose_name="已经出售（本单成交）")  # 已经出售

    img = ForeignKeyField(DarkNet_IMGS, on_delete=None, verbose_name="图片Base64")
    notice = ForeignKeyField(DarkNet_Notice, verbose_name="消息提醒", on_delete="CASCADE")

    class Meta:
        database = db
        indexes = ((("uptime", "user", "title"), True),)


db.connect()
db.create_tables(
    [
        DarkNet_Domain,
        DarkNet_User,
        DarkNet_Saler,
        DarkNet_IMGS,
        DarkNet_Notice,
        DarkNet_DataSale,
    ]
)
