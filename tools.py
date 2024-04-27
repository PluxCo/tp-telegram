import logging
from logging import Logger

from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column, Session

from db_connector import SqlAlchemyBase, DBWorker
from db_connector.types import TextJson

logger = logging.getLogger(__name__)


class SettingsRow(SqlAlchemyBase):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(primary_key=True)
    value = mapped_column(TextJson)


class Settings:
    __instance = None
    __update_handlers = []
    __session: Session = ...
    __storage = {}

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Settings, cls).__new__(cls)

        return cls.__instance

    @classmethod
    def setup(cls, default_values: dict):
        with DBWorker() as db:
            for k, v in default_values.items():
                actual_value = db.get(SettingsRow, k)
                if actual_value is None:
                    db.add(SettingsRow(key=k, value=v))

            db.commit()

        cls.__session = DBWorker().session

        for row in cls.__session.scalars(select(SettingsRow)):
            cls.__storage[row.key] = row

    def __getitem__(self, key):
        return self.__storage[key].value

    def __setitem__(self, key, value):
        self.__storage[key].value = value
        self.notify()

    def __contains__(self, item):
        return item in self.__storage

    def get_storage(self) -> dict:
        return {key: self[key] for key in self.__storage}

    def update(self, data: dict):
        for k, v in data.items():
            self.__storage[k].value = v
        self.notify()

    @classmethod
    def notify(cls):
        logger.info("Updating settings")
        cls.__session.commit()
        for handler in cls.__update_handlers:
            handler()

    @classmethod
    def add_update_handler(cls, handler):
        cls.__update_handlers.append(handler)
