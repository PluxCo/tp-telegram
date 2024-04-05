import logging
from datetime import datetime

from sqlalchemy import select
from telebot.types import CallbackQuery
from telebot.types import Message as TGMessage

from core.feedbacks import MessageUserFeedback, ButtonUserFeedback, ReplyUserFeedback
from core.message import Message
from core.user import User
from db_connector import DBWorker
from scenarios.routing_manager import RFM

from telegram.bot import bot

logger = logging.getLogger(__name__)

manager = RFM()


@bot.message_handler()
def main_handler(message: TGMessage):
    logger.debug(f"Received message: {message}")

    with DBWorker() as db:
        user = db.scalar(select(User).where(User.tg_id == message.from_user.id))

        if user is None:
            user = User(tg_id=message.from_user.id)
            db.add(user)
            db.commit()

    feedback = MessageUserFeedback(message.text, datetime.fromtimestamp(message.date), user)

    manager.handle(feedback)


@bot.callback_query_handler(func=lambda query: True)
def btn_handler(callback_query: CallbackQuery):
    logger.debug(f"Pushed button: {callback_query}")
    bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.id)
    with DBWorker() as db:
        _, message_id, button_id = callback_query.data.split("_")

        message = db.scalar(select(Message).where(Message.id == int(message_id)))

    feedback = ButtonUserFeedback(message, datetime.now(), int(button_id))

    manager.handle(feedback)
