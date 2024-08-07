from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adapter.spi.entity.service_entity import ServiceEntity
from adapter.spi.entity.user_entity import UserEntity
from db_connector import SqlAlchemyBase
from domain.model.session_model import SessionState, Session

logger = logging.getLogger(__name__)


class SessionEntity(SqlAlchemyBase):
    __tablename__ = 'sessions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    service_id: Mapped[str] = mapped_column(ForeignKey('services.id'))

    user: Mapped[UserEntity] = relationship(lazy="joined")
    service: Mapped[ServiceEntity] = relationship(lazy="joined")
    state: Mapped[SessionState] = mapped_column(default=SessionState.OPEN)

    open_time: Mapped[datetime]
    start_time: Mapped[datetime] = mapped_column(nullable=True)
    close_time: Mapped[datetime] = mapped_column(default=datetime.max)

    def __repr__(self):
        return f"SessionEntity({self.id}, {self.user_id}, {self.service_id}, {self.state})"

    def to_model(self):
        return Session(id=self.id,
                       user=self.user.to_model(),
                       service=self.service,
                       state=self.state,
                       open_time=self.open_time,
                       start_time=self.start_time,
                       close_time=self.close_time)

    @staticmethod
    def from_model(s: Session) -> SessionEntity:
        return SessionEntity(id=s.id,
                             user_id=s.user.id,
                             service_id=s.service.id,
                             state=s.state,
                             open_time=s.open_time,
                             start_time=s.start_time,
                             close_time=s.close_time)
