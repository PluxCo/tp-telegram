from __future__ import annotations
import enum
import logging
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, reconstructor

from core.service import Service
from core.sessions.events import SessionEventManager, SessionEventType
from core.user import User
from db_connector import SqlAlchemyBase

logger = logging.getLogger(__name__)


class SessionState(enum.Enum):
    OPEN = 1
    CLOSE = 2


class Session(SqlAlchemyBase):
    __tablename__ = 'sessions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    service_id: Mapped[int] = mapped_column(ForeignKey('services.id'))

    user: Mapped[User] = relationship(lazy="joined")
    service: Mapped[Service] = relationship(lazy="joined")
    state: Mapped[SessionState] = mapped_column(default=SessionState.OPEN)

    open_time: Mapped[datetime]
    close_time: Mapped[datetime] = mapped_column(default=datetime.max)

    def close(self):
        logger.debug(f"Closing session: {self}")
        self.state = SessionState.CLOSE
        self.close_time = datetime.now()
        self.events.notify(self, SessionEventType.STATE_CHANGED)

    def __init__(self, events: SessionEventManager):
        self.events = events

    def __repr__(self):
        return f"Session({self.id}, {self.user_id}, {self.service_id}, {self.state})"

    @reconstructor
    def init_on_load(self):
        self.events = SessionEventManager()
