from uuid import uuid4

import requests
from progressbar import ProgressBar

from conf import Config

media_path = Config.captcha_path
media_path.mkdir(exist_ok=True)

task_nums = 1000 - len(list(media_path.glob("*.png")))
current_nums = 0

bar = ProgressBar(max_value=task_nums)


def get_and_save_captcha(session, url):
    global current_nums
    try:
        resp = session.get(Config.captcha_url)
        if resp.headers.get("Content-Type", "") == "image/png":
            with (media_path / f"{uuid4().hex}.png").open("wb") as pic:
                pic.write(resp.content)
                current_nums += 1
                bar.update(current_nums)
    except Exception as e:
        raise e


session = requests.Session()
session.proxies = {"http": "socks5h://localhost:9150"}

while current_nums < task_nums:
    get_and_save_captcha(session, url)
