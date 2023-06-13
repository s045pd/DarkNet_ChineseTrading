
from os import getenv
from pathlib import Path

from dotenv import load_dotenv

BASE_FOLDER = Path(__file__).parent.parent
ENV_FILE_PATH = BASE_FOLDER / ".env"
SITE_DIR = BASE_FOLDER / "site"
VOL_FOLDER = BASE_FOLDER / "vol"
RESOURCE_DIR = VOL_FOLDER / "resource"
SCREEN_SHOT_PATH = VOL_FOLDER / "screen_shot"


load_dotenv(ENV_FILE_PATH)


def env_bool(var_name: str, defaults: bool = False) -> bool:
    """
    env boolean check
    """
    return str(getenv(var_name, str(defaults))).lower() == "True".lower()


DEBUG = env_bool("DEBUG", True)

# mysql database
USE_MYSQL = env_bool("USE_MYSQL")
MYSQL_DATABASE = getenv("MYSQL_DATABASE", "nlp")
MYSQL_USER = getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = getenv("MYSQL_PASSWORD", "")
MYSQL_HOST = getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT_NUMBER = int(getenv("MYSQL_PORT_NUMBER", "3306"))

# sqlite database path
DATABASE_PATH = getenv("DATABASE_PATH", VOL_FOLDER / "data.db")


# tor config
TOR_PROXY = getenv("TOR_PROXY", "socks5h://localhost:9050")

# tg config
TG_TOKEN = getenv("TG_TOKEN", None)
TG_CHANNEL_ID_DARK_NET = getenv("TG_CHANNEL_ID_DARK_NET", None)
TG_REPORT_GROUP_ID = getenv("TG_REPORT_GROUP_ID", None)
TG_PROXY = getenv("TG_PROXY", None)

# porn image filter
FILTER_PORN_IMAGE = env_bool("FILTER_PORN_IMAGE", False)

# send for test
SEND_FOR_TEST = env_bool("SEND_FOR_TEST", True)

# log config
LOG_LEVEL = getenv("LOG_LEVEL", "INFO")
LOG_FILE = getenv("LOG_FILE", VOL_FOLDER / "log.log")
LOG_FORMAT = getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# redis config
USE_REDIS = env_bool("USE_REDIS")
REDIS_HOST = getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(getenv("REDIS_PORT_NUMBER", "6379"))
REDIS_PASSWORD = getenv("REDIS_PASSWORD", "")
REDIS_DB = getenv("REDIS_DB", "0")
REDIS_URI = getenv(
    "REDIS_URI",
    f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
)
# sqlite cache
CELERY_CACHE_PATH = getenv("CELERY_CACHE_PATH", VOL_FOLDER / "cache.db")