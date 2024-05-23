from datetime import datetime

from sqlalchemy import select, func

from adapter.spi.entity.message_entity import MotivationMessageEntity, ReplyMessageEntity
from core.message import MessageState as EntityMessageState, Message
from db_connector import DBWorker
from domain.model.message_model import SimpleMessageModel, MessageState, MessageWithButtonsModel, \
    MotivationMessageModel, ReplyMessageModel, MessageModel
from domain.model.user_model import UserModel
from port.spi.message_port import CreateMessagePort, SaveMessagePort, GetMessageInTimeIntervalPort
from telegram.messages import SimpleMessage, MessageWithButtons


class DbMessageRepository(CreateMessagePort, SaveMessagePort, GetMessageInTimeIntervalPort):
    def get_messages_count_in_time_interval(self, user, service, begin: datetime, end: datetime) -> int:
        with DBWorker() as db:
            return db.execute(select(func.count(Message.id)).
                              where(Message.date >= begin, Message.date <= end,
                                    Message.user_id == user.id, Message.service_id == service.id)).scalar()

    def create_simple_message(self, user: UserModel, service_id, text) -> SimpleMessageModel:
        with DBWorker() as db:
            m = SimpleMessage(text=text, user_id=user.id, service_id=service_id)

            db.add(m)
            db.commit()

            return SimpleMessageModel(id=m.id, user=user, service_id=service_id, text=text)

    def save_simple_message(self, message: SimpleMessageModel):
        with DBWorker() as db:
            m = db.get(SimpleMessage, message.id)

            m.text = message.text
            m.state = EntityMessageState.TRANSFERRED if message.state == MessageState.SENT else EntityMessageState.PENDING
            m.date = message.date

            db.commit()

    def create_message_with_buttons(self, user: UserModel, service_id, text, buttons) -> MessageWithButtonsModel:
        with DBWorker() as db:
            m = MessageWithButtons(text=text, user_id=user.id, service_id=service_id, buttons=buttons)

            db.add(m)
            db.commit()

            return MessageWithButtonsModel(id=m.id, user=user, service_id=service_id, text=text, buttons=buttons)

    def save_message_with_buttons(self, message: MessageWithButtonsModel):
        with DBWorker() as db:
            m = db.get(MessageWithButtons, message.id)

            m.state = EntityMessageState.TRANSFERRED if message.state == MessageState.SENT else EntityMessageState.PENDING
            m.date = message.date

            db.commit()

    def create_motivation_message(self, user: UserModel, service_id, mood) -> MotivationMessageModel:
        with DBWorker() as db:
            m = MotivationMessageEntity(user_id=user.id, service_id=service_id, mood=mood)

            db.add(m)
            db.commit()

            return m.to_model(user)

    def save_motivation_message(self, message: MotivationMessageModel):
        with DBWorker() as db:
            m = db.get(MotivationMessageEntity, message.id)

            m.state = EntityMessageState.TRANSFERRED if message.state == MessageState.SENT else EntityMessageState.PENDING
            m.date = message.date

            db.commit()

    def create_reply_message(self, user: UserModel, service_id, text, reply_to) -> ReplyMessageModel:
        with DBWorker() as db:
            m = ReplyMessageEntity(user_id=user.id, service_id=service_id, reply_text=text, reply_to=reply_to)

            db.add(m)
            db.commit()

            return m.to_model(user)

    def save_reply_message(self, message: ReplyMessageModel):
        with DBWorker() as db:
            m = db.get(ReplyMessageEntity, message.id)

            m.state = EntityMessageState.TRANSFERRED if message.state == MessageState.SENT else EntityMessageState.PENDING
            m.date = message.date

            db.commit()
