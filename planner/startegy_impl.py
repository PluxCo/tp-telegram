import logging
from datetime import datetime, timedelta

from sqlalchemy import select, func

from core.message import Message
from core.sessions.session import Session
from db_connector import DBWorker
from tools import Settings

logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(self):
        self.__messages_count: int = ...
        self.__time_limit: timedelta = ...

        Settings().add_update_handler(self.update_settings)

    def update_settings(self):
        self.__messages_count = Settings()["amount_of_questions"]
        self.__time_limit = timedelta(seconds=Settings()["session_duration"])

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
