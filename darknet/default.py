from pathlib import Path
import os

current_path = Path("./")

_ = lambda x, y: os.environ.get(x, y) or y
__ = lambda x, y: _(x, str(y)).lower() == str(y).lower()


class Config:
    """
    Default configuration , Can be effetively changed by env variables.
    DEMO:
        export DEBUG=FALSE
        export MYSQL_HOST=192.168.1.1
    """

    debug = __("DEBUG", True)
    domains = (
        _(
            "DOMAIN",
            "xxxxxxxx3a3kuuhhw5w7stk25fzhttrlpiomij5bogkg7yyqsng5tqyd.onion",
        ),
    )

    mysql_host = _("MYSQL_HOST", "127.0.0.1")
    mysql_port = int(_("MYSQL_PORT", "3306"))
    mysql_usr = _("MYSQL_USR", "root")
    mysql_pass = _("MYSQL_PASS", "root")
    mysql_db = _("MYSQL_DB", "db")

    tor_proxy = _("TOR_PROXY", "socks5h://127.0.0.1:9050")

    tg_proxy = _("TG_PROXY", None)
    tg_token = _("TG_TOKEN", None)
    tg_channel_id_darknet = _("TG_CID_DARKNET", None)
    tg_report_group_id = _("TG_REPORT_GID", None)

    no_porn_img = __("NO_PORN", False)
    send_for_test = __("SEND_FOR_TEST", True)

    filter_area = tuple(
        [
            item
            for item in (
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
            if not _("FILTER_AREA", "")
            or item[0].split("=")[1] in _("FILTER_AREA", "")
        ]
    )

    just_update = __("JUST_UPDATE", True)
    screen_path = Path(_("ABS_SCREEN_PATH", current_path / "screen_shot"))
    max_log_len = int(_("MAX_LOG_LEN", "120"))
    limit_log = __("LIMIT_LOG", True)
    notice_range_days = int(_("NOTICE_RANGE_DAYS", "2"))


if __name__ == "__main__":
    from pprint import pprint

    pprint(Config.__dict__)
