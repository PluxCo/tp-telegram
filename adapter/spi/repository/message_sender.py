from sqlalchemy import select
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.message import Message, MessageState as EntityMessageState
from core.user import User
from db_connector import DBWorker
from domain.model.message_model import SimpleMessageModel, MessageModel, MessageState, MessageWithButtonsModel, \
    MotivationMessageModel
from domain.model.user_model import UserModel
from port.spi.message_port import SendMessagePort, GetMessageByInChatIdPort
from telegram.bot import bot
from telegram.messages import SimpleMessage


class TgMessageSender(SendMessagePort, GetMessageByInChatIdPort):
    def send_simple_message(self, message: SimpleMessageModel):
        with DBWorker() as db:
            real_user_id = db.get(User, message.user.id).tg_id

            sent_msg = bot.send_message(real_user_id, message.text)

            entity_message = db.get(Message, message.id)
            entity_message.internal_id = sent_msg.id

            db.commit()

    def send_message_with_buttons(self, message: MessageWithButtonsModel):
        with DBWorker() as db:
            real_user_id = db.get(User, message.user.id).tg_id

            markup = InlineKeyboardMarkup()
            for i, btn in enumerate(message.buttons):
                btn = InlineKeyboardButton(btn, callback_data=f"btn_{message.id}_{i}")
                markup.add(btn)

            sent_msg = bot.send_message(real_user_id, message.text, reply_markup=markup)

            entity_message = db.get(Message, message.id)
            entity_message.internal_id = sent_msg.id

            db.commit()

    def send_motivation_message(self, message: MotivationMessageModel, file_url: str):
        with DBWorker() as db:
            real_user_id = db.get(User, message.user.id).tg_id

            sent_msg = bot.send_video(real_user_id, file_url)

            entity_message = db.get(Message, message.id)
            entity_message.internal_id = sent_msg.id

            db.commit()

    def get_message_by_in_chat_id(self, message_id: int) -> MessageModel:
        # FIXME: Wrong associated types
        with DBWorker() as db:
            message_entity = db.scalar(select(Message).where(Message.internal_id == message_id))

            return MessageModel(id=message_entity.id,
                                user=UserModel(message_entity.user_id),
                                service_id=message_entity.service_id,
                                date=message_entity.date,
                                state=MessageState.SENT if message_entity.state == EntityMessageState.TRANSFERRED else EntityMessageState.PENDING)
