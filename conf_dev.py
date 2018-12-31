class ConfigDev:
    mysql_host = "1.2.3.4"
    mysql_port = 3306
    mysql_usr = 'root'
    mysql_pass = ''
    mysql_db = 'db'

    redis_host = '127.0.0.1'
    redis_port = 6379

    telegram_proxy = None
    telegram_token = "xxxxxxxxxxxxxxxxxxx"
    darknetchannelID = '-100000000000'
    ReportGroupID = '-100000000001'

    tor_proxy = "socks5h://127.0.0.1:9150"
    
    sendForTest = False
    filterArea = ("其它类别","卡料-CVV","基础知识","实体物品","影视-色情","技术-教学","数据-情报","服务-接单","私人专拍","虚拟资源")



Config = ConfigDev
