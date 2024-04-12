import abc
import datetime
import itertools

import numpy as np
from sqlalchemy import select, update

from core.service import Service
from core.sessions.events import SessionEventManager, SessionEventType
from core.sessions.session import Session, SessionState
from core.user import User
from db_connector import DBWorker


class InitSessionStrategy(abc.ABC):
    @abc.abstractmethod
    def selections_probability(self, user: User, service: Service) -> float:
        pass

    def __call__(self, pick_time: datetime):
        self.__pick_time = pick_time
        return self

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__pick_time = None


class SessionAggregator:

    def __init__(self, strategy: InitSessionStrategy, session_event_manager: SessionEventManager):
        self._strategy = strategy

        self.__event_manager = session_event_manager

    def _init_user_session(self, user: User, service: Service):
        with DBWorker() as db:
            user = db.merge(user)
            service = db.merge(service)

            if db.scalar(select(Session).where(Session.user_id == user.id,
                                               Session.state == SessionState.OPEN)):
                return

            session = Session(self.__event_manager)
            session.user = user
            session.service = service
            session.open_time = datetime.datetime.now().replace(microsecond=0)

            db.add(session)
            db.commit()

            self.__event_manager.notify(session, SessionEventType.SESSION_CREATED)

    def initiate_sessions(self, pick_time: datetime):
        with DBWorker() as db:
            users = db.scalars(select(User)).all()
            services = db.scalars(select(Service)).all()

        with self._strategy(pick_time):
            for u in users:
                probs = [self._strategy.selections_probability(u, s) for s in services]
                service_index = np.argmax(probs)

                if probs[service_index] != 0:
                    self._init_user_session(u, services[service_index])
