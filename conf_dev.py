class config_root:
    debug = True
    domain = "xxxxxxxx3a3kuuhhw5w7stk25fzhttrlpiomij5bogkg7yyqsng5tqyd.onion"

    mysql_host = "127.0.0.1"
    mysql_port = 3306
    mysql_usr = "root"
    mysql_pass = ""
    mysql_db = "db"

    redis_host = "127.0.0.1"
    redis_port = 6379

    tor_proxy = "socks5h://127.0.0.1:9150"

    tg_proxy = None
    tg_token = "xxxxxxxxxxxxxxxxxxx"
    tg_channel_id_darknet = "-100000000000"
    tg_report_group_id = "-000000000"

    no_porn_img = False
    send_for_test = True

    filter_area = (
        ("/ea.php?ea=10001", "数据资源"),
        ("/ea.php?ea=10006", "服务业务"),
        ("/ea.php?ea=10002", "虚拟物品"),
        ("/ea.php?ea=10007", "实体物品"),
        ("/ea.php?ea=10003", "技术技能"),
        ("/ea.php?ea=10004", "影视色情"),
        ("/ea.php?ea=10010", "其它类别"),
        ("/ea.php?ea=10005", "基础知识"),
        ("/ea.php?ea=10009", "私人专拍"),
    )


    send_for_test = False
    just_update = True

    screen_path = current_path / "screen_shot"

    max_log_len = 120
    limit_log = True

    notice_range_days = 2



Config = config_root
