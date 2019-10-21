class ConfigDev:
    debug = True
    mysql_host = "1.2.3.4"
    mysql_port = 3306
    mysql_usr = "root"
    mysql_pass = ""
    mysql_db = "db"

    redis_host = "127.0.0.1"
    redis_port = 6379

    telegram_proxy = None
    telegram_token = "xxxxxxxxxxxxxxxxxxx"
    darknetchannelID = "-100000000000"
    ReportGroupID = "-100000000001"

    tor_proxy = "socks5h://127.0.0.1:9150"

    sendForTest = False
    no_porn_img = True
    filterArea = ("其它", "卡料", "基础", "实体", "影视", "技术", "数据", "服务", "私拍", "虚拟")


Config = ConfigDev
