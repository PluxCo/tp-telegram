from __future__ import annotations

import enum

from sqlalchemy.orm import Mapped, MappedColumn

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

    id: Mapped[int] = MappedColumn(primary_key=True, autoincrement=True)
    type: Mapped[str]

    def send(self) -> SendingStatus:
        raise NotImplemented("Method should be implemented")
