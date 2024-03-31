import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, reconstructor

from core.service import Service
from core.sessions.events import SessionEventManager
from core.user import User
from db_connector import SqlAlchemyBase


class SessionState(enum.Enum):
    OPEN = 1
    CLOSE = 2


class Session(SqlAlchemyBase):
    __tablename__ = 'sessions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    service_id: Mapped[int] = mapped_column(ForeignKey('services.id'))

    user: Mapped[User] = relationship()
    service: Mapped[Service] = relationship()
    state: Mapped[SessionState] = mapped_column(default=SessionState.OPEN)

    def close(self):
        self.state = SessionState.CLOSE

    def __init__(self, events: SessionEventManager):
        self.events = events

    @reconstructor
    def init_on_load(self):
        self.events = SessionEventManager()
