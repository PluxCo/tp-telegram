from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from core.user import User
from db_connector import SqlAlchemyBase


class MessageState(enum.Enum):
    TRANSFERRED = 1
    PENDING = 2


class SendingStatus:
    def __init__(self, message: Message, state: MessageState):
        self.message = message
        self.state = state


class Message(SqlAlchemyBase):
    __tablename__ = 'messages'
    __mapper_args__ = {'polymorphic_identity': 'message', "polymorphic_on": "type"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str]

    handler: Mapped[str] = mapped_column(nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped[User] = relationship(lazy="joined")

    internal_id: Mapped[int] = mapped_column(nullable=True)

    date: Mapped[datetime] = mapped_column(nullable=True)

    def send(self) -> SendingStatus:
        raise NotImplemented("Method should be implemented")
