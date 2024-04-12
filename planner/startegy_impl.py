from datetime import datetime, timedelta, time

from sqlalchemy import select, func

from core.message import Message
from core.service import Service
from core.sessions.aggregation import InitSessionStrategy
from core.sessions.session import Session
from core.user import User
from db_connector import DBWorker
from tools import Settings


class SimpleWindowSessionStrategy(InitSessionStrategy):
    def __init__(self):
        self.__prev_call = datetime.min

        self.__period: timedelta = ...
        self.__from: time = ...
        self.__to: time = ...

        self.update_settings()

        Settings().add_update_handler(self.update_settings)

        self.__pick_time = None

    def update_settings(self):
        stg = Settings()

        self.__period = timedelta(seconds=stg["period"])
        self.__from = time.fromisoformat(stg["start_time"])
        self.__to = time.fromisoformat(stg["end_time"])

    def selections_probability(self, user: User, service: Service) -> float:
        if self.__pick_time - self.__prev_call < self.__period:
            return 0

        if self.__pick_time.time() < self.__from or datetime.now().time() > self.__to:
            return 0

        return 1

    def __call__(self, pick_time: datetime):
        self.__pick_time = pick_time
        return self

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__prev_call = self.__pick_time


class SessionManager:
    def __init__(self, messages_count: int, time_limit: timedelta):
        self.__messages_count = messages_count
        self.__time_limit = time_limit

    def is_neccessary_to_close(self, session: Session) -> bool:
        with DBWorker() as db:
            messages_count = db.scalar(select(func.count(Message.id)).
                                       where(Message.date > session.open_time,
                                             Message.date < session.close_time))

            if messages_count >= self.__messages_count:
                return True

            if datetime.now() - session.open_time > self.__time_limit:
                return True

        return False
