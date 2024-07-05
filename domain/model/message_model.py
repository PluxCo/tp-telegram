from __future__ import annotations

import abc
import enum

from dataclasses import dataclass
from datetime import datetime

from domain.model.user_model import UserModel


class MessageState(enum.Enum):
    PENDING = 0
    SENT = 1
    CANCELED = 2


@dataclass(kw_only=True)
class MessageModel(abc.ABC):
    id: int = None

    user: UserModel
    service_id: str = None

    date: datetime = None
    state: MessageState = MessageState.PENDING

    def send(self):
        self.state = MessageState.SENT
        self.date = datetime.now()

    @abc.abstractmethod
    def accept(self, visitor: MessageVisitor):
        pass


@dataclass(kw_only=True)
class SimpleMessageModel(MessageModel):
    text: str

    def accept(self, visitor: MessageVisitor):
        visitor.visit_simple_message(self)


@dataclass(kw_only=True)
class MessageWithButtonsModel(MessageModel):
    text: str
    buttons: list[str]

    def accept(self, visitor: MessageVisitor):
        visitor.visit_message_with_buttons(self)


@dataclass(kw_only=True)
class MotivationMessageModel(MessageModel):
    mood: str

    def accept(self, visitor: MessageVisitor):
        visitor.visit_motivation_message(self)


@dataclass(kw_only=True)
class ReplyMessageModel(MessageModel):
    text: str
    reply_to: int

    def accept(self, visitor: MessageVisitor):
        visitor.visit_reply_message(self)


class MessageVisitor(abc.ABC):
    @abc.abstractmethod
    def visit_simple_message(self, message: SimpleMessageModel):
        pass

    @abc.abstractmethod
    def visit_message_with_buttons(self, message: MessageWithButtonsModel):
        pass

    @abc.abstractmethod
    def visit_motivation_message(self, message: MotivationMessageModel):
        pass

    @abc.abstractmethod
    def visit_reply_message(self, message: ReplyMessageModel):
        pass
