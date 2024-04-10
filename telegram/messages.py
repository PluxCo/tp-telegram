import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Mapped, mapped_column
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.message import Message, SendingStatus, MessageState
from core.service import Service
from core.user import User
from db_connector.types import TextJson
from telegram.bot import bot

logger = logging.getLogger(__name__)


class SimpleMessage(Message):
    """
    Simple message without any features. Implements :class:`Message`
    """

    __mapper_args__ = {'polymorphic_identity': 'simple'}

    text: Mapped[str] = mapped_column(nullable=True)

    def __init__(self, user: User, text: str, service: Service = None, **kw):
        """
        :param user: User that should receive a message
        :param text: text of a message
        :param service: service which as a sender
        """
        self.user = user
        self.service = service

        self.text = text

        super().__init__(**kw)

    def send(self) -> SendingStatus:
        tg_msg = bot.send_message(self.user.tg_id, text=self.text)
        self.date = datetime.fromtimestamp(tg_msg.date)
        self.internal_id = tg_msg.id

        self._status = SendingStatus(MessageState.TRANSFERRED)
        return self.status


class MessageWithButtons(SimpleMessage):
    __mapper_args__ = {'polymorphic_identity': 'buttons'}

    buttons = mapped_column(TextJson, nullable=True)

    def send(self) -> SendingStatus:
        markup = InlineKeyboardMarkup()
        for i, btn in enumerate(self.buttons):
            btn = InlineKeyboardButton(btn, callback_data=f"btn_{self.id}_{i}")
            markup.add(btn)

        tg_msg = bot.send_message(self.user.tg_id, text=self.text, reply_markup=markup)

        self.date = datetime.fromtimestamp(tg_msg.date)
        self.internal_id = tg_msg.id

        self._status = SendingStatus(MessageState.TRANSFERRED)
        return self.status
