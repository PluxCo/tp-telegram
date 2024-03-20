import datetime
import logging
import os
import time
from threading import Thread

from requests import get

from models.db_session import create_session
from models.user import User
from models.sessions import Session
from tools import Settings
from bot.bot import send_messages

# FIXME: God rewrite this weird Schedule by using basic python module.

class Schedule(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._callback = None

        self._every = None
        self._week_days = None
        self._from_time = None
        self._to_time = None
        Settings().add_update_handler(self.from_settings)

        self.previous_call = None


    def from_settings(self):
        self._every = Settings()['time_period']
        self._week_days = Settings()['week_days']
        self._from_time = Settings()['from_time']
        self._to_time = Settings()['to_time']

        return self

    def run(self) -> None:
        """The run function of a schedule thread. Note that the order in which you call methods matters.
         on().every() and every().on() play different roles. They in somewhat way mask each-other."""
        while True:
            now = datetime.datetime.now()

            question_for_person = []
            if self._from_time is None or self._from_time <= now.time() <= self._to_time:
                if self.previous_call is None or (now >= self.previous_call + self._every):
                    self.previous_call = now
                    if self._week_days is None or now.weekday() in self._week_days:
                        self.task()
                        self.previous_call = now

            time.sleep(1)

    def task(self):
        try:
            users_sessions = []
            with create_session() as db:
                # getting new users without started sessions
                people = db.query(User).where(User.tg_id.notin_(db.query(Session.user_tg_id))).all()
                for person in people:
                    # Requesting questions not ended
                    webhook = ''
                    request = get(webhook).json()
                    webhook = request["webhook"]
                    messages = request["messages"]
                    session = Session(person)
                    session.generate_questions()
                    users_sessions.append(session)
                    print(person)

        except Exception as e:
            logging.exception(e)