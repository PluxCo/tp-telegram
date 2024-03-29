import datetime
import itertools
import logging
import os
import time
from threading import Thread

from requests import get
from sqlalchemy import or_, and_, select

from bot.bot import ping_message
from bot.models.telegram_types import SessionState
from models.db_session import create_session
from models.message import Message
from models.sessions import Session
from models.user import User
from tools import Settings


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
        self._every = datetime.timedelta(seconds=Settings()['time_period'])
        self._week_days = Settings()['week_days']
        self._from_time = datetime.time.fromisoformat(Settings()['from_time'])
        self._to_time = datetime.time.fromisoformat(Settings()['to_time'])

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
                new_people_db = db.query(User.auth_id).where(User.tg_id.notin_(db.query(Session.user_tg_id))).all()
                people = new_people_db
                closed_sessions_people_db = db.query(User.tg_id, User.auth_id).where(and_(User.tg_id.notin_(
                    db.query(Session.user_tg_id).where(or_(Session.session_state == SessionState.OPEN.value,
                                                           Session.session_state == SessionState.PENDING.value))),
                    User.tg_id.in_(db.query(Session.user_tg_id)))).all()
                for closed_person_tg_id, closed_person_auth_id in closed_sessions_people_db:
                    logging.debug(f"closed person id: {closed_person_auth_id} with type {type(closed_person_auth_id)}")
                    last_session_time = db.scalar(
                        select(Session.opening_time).where(Session.user_tg_id == closed_person_tg_id).order_by(
                            Session.opening_time.desc()))
                    if (datetime.datetime.now() - last_session_time) >= self._every:
                        people.append(closed_person_auth_id)
                pending_users = db.query(Message.message_id, Message.tg_id).where(
                    and_(Session.session_state == SessionState.PENDING.value, Message.session_id == Session.id)).all()

                if pending_users:
                    ping_message(pending_users)

                # people = list(itertools.chain(*people))
                # Requesting questions not ended
                for i in range(len(people)):
                    # Damn...
                    if not isinstance(people[i], str):
                        people[i] = people[i][0]

                logging.debug(f"users to send: {people}")
                webhook = Settings()["webhook"]
                body = {"users_ids": people, "webhook": os.environ["TELEGRAM_API"] + "/message/"}
                logging.debug(f"Request to webhook: {body}")
                get(webhook, json=body)

        except Exception as e:
            logging.exception(e)
