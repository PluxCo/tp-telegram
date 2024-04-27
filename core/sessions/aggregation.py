from __future__ import annotations

import logging
from datetime import datetime, timedelta, time

from sqlalchemy import select

from core.service import Service
from core.sessions.events import SessionEventManager, SessionEventType
from core.sessions.session import Session, SessionState
from core.user import User
from db_connector import DBWorker
from scenarios import routing_manager
from tools import Settings

logger = logging.getLogger(__name__)


class SessionAggregator:

    def __init__(self, session_event_manager: SessionEventManager):
        self.__event_manager = session_event_manager

        self.__prev_call = datetime.min

        self.__period: timedelta = ...
        self.__from: time = ...
        self.__to: time = ...

        self.update_settings()

        Settings().add_update_handler(self.update_settings)

    def update_settings(self):
        stg = Settings()

        self.__period = timedelta(seconds=stg["period"])
        self.__from = time.fromisoformat(stg["start_time"])
        self.__to = time.fromisoformat(stg["end_time"])

        logger.debug(f"Updating strategy settings (from: {self.__from}, to: {self.__to}, period: {self.__period})")

    def _init_user_session(self, user: User, service: Service):
        with DBWorker() as db:
            user = db.merge(user)
            service = db.merge(service)

            logger.debug(f"Initializing session between {user} and {service}")

            if db.scalar(select(Session).where(Session.user_id == user.id,
                                               Session.state == SessionState.OPEN)):
                return

            session = Session(self.__event_manager)
            session.user = user
            session.service = service
            session.open_time = datetime.now().replace(microsecond=0)

            db.add(session)
            db.commit()

            session = db.get(Session, session.id)

            self.__event_manager.notify(session, SessionEventType.SESSION_CREATED)

    def initiate_sessions(self, pick_time: datetime):
        with DBWorker() as db:
            users = db.scalars(select(User)).all()
            services = db.scalars(select(Service)).all()

            sessions = db.scalars(select(Session).where(Session.state == SessionState.OPEN))

            for session in sessions:
                if routing_manager.session_manager.is_neccessary_to_close(session):
                    session.close()

            db.commit()

        if pick_time - self.__prev_call < self.__period:
            return

        if pick_time.time() < self.__from or datetime.now().time() > self.__to:
            return

        for u in users:
            for s in services:
                self._init_user_session(u, s)

        self.__prev_call = pick_time
