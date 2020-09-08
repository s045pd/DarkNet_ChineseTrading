from dataclasses import dataclass
from uuid import uuid4

import asks
import trio
from progressbar import ProgressBar

domain = "xxxxxxxx3a3kuuhhw5w7stk25fzhttrlpiomij5bogkg7yyqsng5tqyd.onion"
asks.init("trio")


@dataclass
class worker:
    conns = 1
    task_nums = 1000
    current_nums = 0
    media_path = trio.Path(str(Config.captcha_path))
    url = f"http://{domain}/entrance/code76.php"

    async def init(self):
        await self.media_path.mkdir(exist_ok=True)
        self.bar = ProgressBar(max_value=self.task_nums)
        self.session = asks.Session(connections=self.conns)
        # self.session.proxies = {"http": "socks5h://localhost:9150"}
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Upgrade-Insecure-Requests": "1",
        }
        self.limit = trio.CapacityLimiter(self.conns * 1)

    async def get_and_save_captcha(self):
        async with self.limit:
            try:
                print(self.current_nums)
                resp = await self.session.get(self.url)
                if resp.headers.get("Content-Type", "") == "image/png":
                    async with (media_path / f"{uuid4().hex}.png").open("wb") as pic:
                        await pic.write_bytes(resp.content)
                        self.current_nums += 1
                        self.bar.update(self.current_nums)
            except Exception as e:
                raise e

    async def patch_tasks(self):
        async with trio.open_nursery() as nursery:
            [
                nursery.start_soon(self.get_and_save_captcha)
                for _ in range(self.task_nums)
            ]

    async def fetch_main(self):
        resp = await self.session.get(f"http://{domain}")
        print(resp.text)

    def start(self):
        trio.run(self.init)
        trio.run(self.fetch_main)
        trio.run(self.patch_tasks)


worker().start()
