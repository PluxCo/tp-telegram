from datetime import datetime

from sqlalchemy import select, func

from adapter.spi.entity.message_entity import MotivationMessageEntity, ReplyMessageEntity, SimpleMessageEntity, \
    MessageWithButtonsEntity, MessageEntity

from adapter.spi.entity.message_entity import MessageEntity as Message
from db_connector import DBWorker
from domain.model.message_model import SimpleMessageModel, MessageWithButtonsModel, \
    MotivationMessageModel, ReplyMessageModel, MessageModel
from domain.model.user_model import UserModel
from port.spi.message_port import SaveMessagePort, GetMessageInTimeIntervalPort


class DbMessageRepository(SaveMessagePort, GetMessageInTimeIntervalPort):
    def get_messages_count_in_time_interval(self, user, service, begin: datetime, end: datetime) -> int:
        with DBWorker() as db:
            return db.execute(select(func.count(Message.id)).
                              where(Message.date >= begin, Message.date <= end,
                                    Message.user_id == user.id, Message.service_id == service.id)).scalar()

    def save_message(self, message: MessageModel) -> MessageModel:
        with DBWorker() as db:
            message_entity = MessageEntity.from_model(message)
            message_entity = db.merge(message_entity)
            db.commit()

            return message_entity.to_model()
