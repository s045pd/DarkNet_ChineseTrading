import random

import moment
from peewee import fn

from darknet.common import error_log
from darknet.log import warning
from darknet.model import events, workers


class Cursor:
    @staticmethod
    @error_log()
    def create_new_user(auth):
        return workers.create(**{"usr": auth[0], "pwd": auth[1]})

    @staticmethod
    @error_log()
    def get_random_user(last_days=30):
        users = (
            workers.select()
            .where(
                workers.useful == True,
                workers.intime >= moment.now().add(days=-last_days).format("YYYY-MM-DD HH:mm:ss"),
            )
            .order_by(fn.Rand())
            .limit(10)
        )
        return random.choice(users) if users else None

    @staticmethod
    @error_log()
    def ban_user(usr):
        warning(f"ban user: {usr}")
        return workers.update({"useful": False}).where(workers.usr == usr).execute()

    @staticmethod
    @error_log()
    def get_model_details(sid):
        details = events.select().where((events.sid == sid))
        return details

    @staticmethod
    @error_log()
    def create_details(datas):
        return events.create(**datas)

    @staticmethod
    @error_log()
    def update_details(datas, sid):
        events.update(datas).where((events.sid == sid)).execute()

    @staticmethod
    @error_log()
    def obj_max_id(obj, ids="id"):
        return obj.select(fn.Max(obj["ids"])).scalar() + 1
