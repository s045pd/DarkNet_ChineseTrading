import datetime

import pymysql
from peewee import *
from peewee import __exception_wrapper__

from darknet.default import Config

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
            cursor = super(RetryOperationalError, self).execute_sql(
                sql, params, commit
            )
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


class workers(Model):
    usr = CharField(max_length=20, primary_key=True, verbose_name="用户ID")
    pwd = CharField(max_length=20, verbose_name="密码")
    useful = BooleanField(default=True)
    intime = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


class events(Model):
    sid = IntegerField(primary_key=True, verbose_name="交易编号")
    uptime = DateTimeField(verbose_name="交易发布时间")
    lasttime = DateTimeField(verbose_name="商家最后在线")
    user = CharField(max_length=20, verbose_name="卖家账号", default="")
    title = CharField(max_length=155, verbose_name="发布标题")
    priceBTC = FloatField(verbose_name="单价折算")
    priceUSDT = FloatField(verbose_name="商品单价")
    link = CharField(max_length=255, verbose_name="详情地址")
    area = CharField(max_length=32, verbose_name="交易类型")
    status = CharField(max_length=32, verbose_name="交易状态")
    sold = IntegerField(verbose_name="本单成交", default=0)
    text = TextField(default="", verbose_name="商品描述")
    # img = TextField(default="", verbose_name="图片Base64组合")

    intime = DateTimeField(
        default=datetime.datetime.now, verbose_name="数据插入时间"
    )
    notice = BooleanField(default=False, verbose_name="任意提醒标识")

    class Meta:
        database = db
        indexes = ((("uptime", "user", "title"), True),)


db.connect()
db.create_tables(
    [
        workers,
        events,
    ]
)

# db.execute_sql("ALTER TABLE events MODIFY img LONGTEXT NOT NULL;")
# db.execute_sql("ALTER TABLE DarkNet_Saler AUTO_INCREMENT={}".format( ))
