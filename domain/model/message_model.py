import enum
from abc import ABC
from dataclasses import dataclass
from datetime import datetime

from domain.model.user_model import UserModel


class MessageState(enum.Enum):
    PENDING = 0
    SENT = 1
    CANCELED = 2


@dataclass(kw_only=True)
class MessageModel(ABC):
    id: int

    user: UserModel
    service_id: int

    date: datetime = None
    state: MessageState = MessageState.PENDING

    def send(self):
        self.state = MessageState.SENT
        self.date = datetime.now()


@dataclass(kw_only=True)
class SimpleMessageModel(MessageModel):
    text: str


@dataclass(kw_only=True)
class MessageWithButtonsModel(MessageModel):
    text: str
    buttons: list[str]


@dataclass(kw_only=True)
class MotivationMessageModel(MessageModel):
    mood: str
