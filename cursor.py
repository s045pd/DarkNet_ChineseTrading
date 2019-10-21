import moment
import peewee
from model import (
    DarkNet_Domain,
    DarkNet_DataSale,
    DarkNet_IMGS,
    DarkNet_Notice,
    DarkNet_Saler,
    DarkNet_User,
)
from peewee import fn
from log import info, error, warning, debug


class Cursor:
    @staticmethod
    def get_last_domain():
        try:
            return (
                DarkNet_Domain.select()
                .order_by(DarkNet_Domain.datetime)
                .limit(1)[0]
                .domain
            )
        except Exception as e:
            error(f"[Cursor->get_last_domain]: {e}")

    @staticmethod
    def create_new_domain(domain):
        try:
            return DarkNet_Domain.create(**{"domain": domain})
        except peewee.IntegrityError:
            pass

    @staticmethod
    def create_new_user(datas):
        return DarkNet_User.create(**datas)

    @staticmethod
    def get_random_user(last_days=30):
        try:
            return (
                DarkNet_User.select()
                .where(
                    DarkNet_User.useful == True,
                    DarkNet_User.intime
                    >= moment.now().add(days=-last_days).format("YYYY-MM-DD HH:mm:ss"),
                )
                .order_by(fn.Rand())
                .limit(10)[0]
            )
        except Exception as e:
            error(f"[Cursor->get_random_user]: {e}")

    @staticmethod
    def ban_user(usr):
        warning(f"ban user: {usr}")
        return (
            DarkNet_User.update({"useful": False})
            .where(DarkNet_User.user == usr)
            .execute()
        )

    @staticmethod
    def get_model_details(uid, sid):
        details = DarkNet_DataSale.select().where((DarkNet_DataSale.sid == sid))
        person = DarkNet_Saler.select().where((DarkNet_Saler.uid == uid))
        notice = DarkNet_Notice.select().where((DarkNet_Notice.sid == sid))
        img = DarkNet_IMGS.select().where((DarkNet_IMGS.sid == sid))
        return details, person, notice, img

    @staticmethod
    def create_person(datas):
        return DarkNet_Saler.create(**datas)

    @staticmethod
    def update_person(datas, uid):
        return DarkNet_Saler.update(datas).where((DarkNet_Saler.uid == uid)).execute()

    @staticmethod
    def create_notice(datas):
        return DarkNet_Notice.create(**datas)

    @staticmethod
    def create_img(datas):
        return DarkNet_IMGS.create(**datas)

    @staticmethod
    def create_details(datas):
        return DarkNet_DataSale.create(**datas)

    @staticmethod
    def update_details(datas, sid):
        DarkNet_DataSale.update(datas).where((DarkNet_DataSale.sid == sid)).execute()
