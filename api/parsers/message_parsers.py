import enum
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.message import Message
from core.service import Service
from core.user import User
from db_connector import DBWorker
from telegram.messages import SimpleMessage, MessageWithButtons


class MessageType(enum.Enum):
    SIMPLE = 1
    WITH_BUTTONS = 2
    MOTIVATION = 3


class Mood(enum.Enum):
    GOOD = 1
    BAD = 2


class MessageCreator:
    def __init__(self, service: Service):
        self.__service: Service = service

    def create_message(self, data: dict, db_session: Session) -> Optional[Message]:
        parsed_user_id = data["user_id"]
        parsed_type = MessageType[data["type"]]

        user = db_session.scalar(select(User).where(User.external_id == parsed_user_id))

        match parsed_type:
            case MessageType.SIMPLE:
                parsed_text = data["text"]

                return SimpleMessage(user=user, text=parsed_text, service=self.__service)

            case MessageType.WITH_BUTTONS:
                parsed_text = data["text"]
                parsed_buttons = data["buttons"]

                return MessageWithButtons(user=user, text=parsed_text, service=self.__service, buttons=parsed_buttons)

            case MessageType.MOTIVATION:
                parsed_mood = Mood[data["mood"]]


class StatusSerializer:
    def dump_status(self, message: Message):
        return {
            "message_id": message.id,
            "state": message.state.name
        }
