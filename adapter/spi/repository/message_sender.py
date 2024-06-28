from sqlalchemy import select
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from adapter.spi.entity.message_entity import MessageEntity
from adapter.spi.entity.user_entity import UserEntity
from db_connector import DBWorker
from domain.model.message_model import SimpleMessageModel, MessageModel, MessageState, MessageWithButtonsModel, \
    MotivationMessageModel, ReplyMessageModel

from port.spi.message_port import SendMessagePort, GetMessageByInChatIdPort


class TgMessageSender(SendMessagePort, GetMessageByInChatIdPort):
    def __init__(self, bot: TeleBot):
        self.bot = bot

    def send_simple_message(self, message: SimpleMessageModel):
        with DBWorker() as db:
            real_user_id = db.get(UserEntity, message.user.id).tg_id

            sent_msg = self.bot.send_message(real_user_id, message.text)

            entity_message = db.get(MessageEntity, message.id)
            entity_message.internal_id = sent_msg.id

            db.commit()

    def send_message_with_buttons(self, message: MessageWithButtonsModel):
        with DBWorker() as db:
            real_user_id = db.get(UserEntity, message.user.id).tg_id

            markup = InlineKeyboardMarkup()
            for i, btn in enumerate(message.buttons):
                btn = InlineKeyboardButton(btn, callback_data=f"btn_{message.id}_{i}")
                markup.add(btn)

            sent_msg = self.bot.send_message(real_user_id, message.text, reply_markup=markup)

            entity_message = db.get(MessageEntity, message.id)
            entity_message.internal_id = sent_msg.id

            db.commit()

    def send_motivation_message(self, message: MotivationMessageModel, file_url: str):
        with DBWorker() as db:
            real_user_id = db.get(UserEntity, message.user.id).tg_id

            sent_msg = self.bot.send_video(real_user_id, file_url)

            entity_message = db.get(MessageEntity, message.id)
            entity_message.internal_id = sent_msg.id

            db.commit()

    def send_reply_message(self, message: ReplyMessageModel):
        with DBWorker() as db:
            real_user_id = db.get(UserEntity, message.user.id).tg_id
            reply_to_id = db.get(MessageEntity, message.reply_to).internal_id

            sent_msg = self.bot.send_message(real_user_id, message.text, reply_to_message_id=reply_to_id)

            entity_message = db.get(MessageEntity, message.id)
            entity_message.internal_id = sent_msg.id

            db.commit()

    def get_message_by_in_chat_id(self, message_id: int) -> MessageModel:
        with DBWorker() as db:
            message_entity: MessageEntity = db.scalar(
                select(MessageEntity).where(MessageEntity.internal_id == message_id))

            return message_entity.to_model()
