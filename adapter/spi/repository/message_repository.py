from datetime import datetime

from sqlalchemy import select, func

from adapter.spi.entity.message_entity import MotivationMessageEntity, ReplyMessageEntity, SimpleMessageEntity, \
    MessageWithButtonsEntity, MessageEntity

from adapter.spi.entity.message_entity import MessageEntity as Message
from db_connector import DBWorker
from domain.model.message_model import SimpleMessageModel, MessageWithButtonsModel, \
    MotivationMessageModel, ReplyMessageModel, MessageModel
from domain.model.user_model import UserModel
from port.spi.message_port import CreateMessagePort, SaveMessagePort, GetMessageInTimeIntervalPort


class DbMessageRepository(CreateMessagePort, SaveMessagePort, GetMessageInTimeIntervalPort):
    def get_messages_count_in_time_interval(self, user, service, begin: datetime, end: datetime) -> int:
        with DBWorker() as db:
            return db.execute(select(func.count(Message.id)).
                              where(Message.date >= begin, Message.date <= end,
                                    Message.user_id == user.id, Message.service_id == service.id)).scalar()

    def create_simple_message(self, user: UserModel, service_id, text) -> SimpleMessageModel:
        with DBWorker() as db:
            m = SimpleMessageEntity(text=text, user_id=user.id, service_id=service_id)

            db.add(m)
            db.commit()

            return m.to_model()

    def save_simple_message(self, message: SimpleMessageModel):
        with DBWorker() as db:
            m = db.get(SimpleMessageEntity, message.id)

            m.text = message.text
            m.state = message.state
            m.date = message.date

            db.commit()

    def create_message_with_buttons(self, user: UserModel, service_id, text, buttons) -> MessageWithButtonsModel:
        with DBWorker() as db:
            m = MessageWithButtonsEntity(text=text, user_id=user.id, service_id=service_id, buttons=buttons)

            db.add(m)
            db.commit()

            return m.to_model()

    def save_message_with_buttons(self, message: MessageWithButtonsModel):
        with DBWorker() as db:
            m = db.get(MessageWithButtonsEntity, message.id)

            m.state = message.state
            m.date = message.date

            db.commit()

    def create_motivation_message(self, user: UserModel, service_id, mood) -> MotivationMessageModel:
        with DBWorker() as db:
            m = MotivationMessageEntity(user_id=user.id, service_id=service_id, mood=mood)

            db.add(m)
            db.commit()

            return m.to_model()

    def save_motivation_message(self, message: MotivationMessageModel):
        with DBWorker() as db:
            m = db.get(MotivationMessageEntity, message.id)

            m.state = message.state
            m.date = message.date

            db.commit()

    def create_reply_message(self, user: UserModel, service_id, text, reply_to) -> ReplyMessageModel:
        with DBWorker() as db:
            m = ReplyMessageEntity(user_id=user.id, service_id=service_id, reply_text=text, reply_to=reply_to)

            db.add(m)
            db.commit()

            return m.to_model()

    def save_reply_message(self, message: ReplyMessageModel):
        with DBWorker() as db:
            m = db.get(ReplyMessageEntity, message.id)

            m.state = message.state
            m.date = message.date

            db.commit()

    def save_message(self, message: MessageModel) -> MessageModel:
        with DBWorker() as db:
            message_entity = MessageEntity.from_model(message)
            message_entity = db.merge(message_entity)
            db.commit()

            return message_entity.to_model()
