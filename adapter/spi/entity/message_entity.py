from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adapter.spi.entity.user_entity import UserEntity
from adapter.spi.entity.service_entity import ServiceEntity
from db_connector import SqlAlchemyBase
from db_connector.types import TextJson
from domain.model.message_model import MotivationMessageModel, MessageState, ReplyMessageModel, SimpleMessageModel, \
    MessageWithButtonsModel, MessageModel
from domain.model.user_model import UserModel


class MessageEntity(SqlAlchemyBase):
    """
    An abstract message

    :cvar id: Index of message
    :cvar user: User that should receive that message
    :cvar service: Service which is a sender
    :cvar internal_id: Telegram message id
    :cvar date: Sending timestamp
    """
    __tablename__ = 'messages'
    __mapper_args__ = {'polymorphic_identity': 'message', "polymorphic_on": "type"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str]

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    service_id: Mapped[str] = mapped_column(ForeignKey("services.id"), nullable=True)
    user: Mapped[UserEntity] = relationship(lazy="joined")
    service: Mapped[ServiceEntity] = relationship(lazy="joined")

    internal_id: Mapped[int] = mapped_column(nullable=True)

    date: Mapped[datetime] = mapped_column(nullable=True)
    state: Mapped[MessageState] = mapped_column(default=MessageState.PENDING)

    def to_model(self):
        raise NotImplementedError()

    @classmethod
    def from_model(cls, model: MessageModel) -> MessageEntity:
        if isinstance(model, SimpleMessageModel):
            return SimpleMessageEntity.from_model(model)
        if isinstance(model, MessageWithButtonsModel):
            return MessageWithButtonsEntity.from_model(model)
        if isinstance(model, MotivationMessageModel):
            return MotivationMessageEntity.from_model(model)
        if isinstance(model, ReplyMessageModel):
            return ReplyMessageEntity.from_model(model)

        raise NotImplementedError(f"Cant resolve '{type(model)} model'")


class SimpleMessageEntity(MessageEntity):
    """
    Simple message without any features. Implements :class:`Message`
    """

    __mapper_args__ = {'polymorphic_identity': 'simple'}

    text: Mapped[str] = mapped_column(nullable=True)

    def to_model(self):
        return SimpleMessageModel(id=self.id, user=self.user.to_model(), service_id=self.service_id,
                                  date=self.date, state=self.state, text=self.text)

    @classmethod
    def from_model(cls, model: SimpleMessageModel) -> SimpleMessageEntity:
        return SimpleMessageEntity(text=model.text,
                                   id=model.id,
                                   user_id=model.user.id,
                                   service_id=model.service_id,
                                   date=model.date,
                                   state=model.state)


class MessageWithButtonsEntity(SimpleMessageEntity):
    __mapper_args__ = {'polymorphic_identity': 'buttons'}

    buttons = mapped_column(TextJson, nullable=True)

    def to_model(self):
        return MessageWithButtonsModel(id=self.id, user=self.user.to_model(), service_id=self.service_id,
                                       date=self.date, state=self.state, text=self.text, buttons=self.buttons)

    @classmethod
    def from_model(cls, model: MessageWithButtonsModel) -> MessageWithButtonsEntity:
        return MessageWithButtonsEntity(buttons=model.buttons,
                                        text=model.text,
                                        id=model.id,
                                        user_id=model.user.id,
                                        service_id=model.service_id,
                                        date=model.date,
                                        state=model.state)


class MotivationMessageEntity(MessageEntity):
    __mapper_args__ = {'polymorphic_identity': 'motivation'}

    mood: Mapped[str] = mapped_column(nullable=True)

    def to_model(self) -> MotivationMessageModel:
        return MotivationMessageModel(id=self.id, user=self.user.to_model(), service_id=self.service_id,
                                      date=self.date,
                                      state=self.state,
                                      mood=self.mood)

    @classmethod
    def from_model(cls, model: MotivationMessageModel) -> MotivationMessageEntity:
        return MotivationMessageEntity(mood=model.mood,
                                       id=model.id,
                                       user_id=model.user.id,
                                       service_id=model.service_id,
                                       date=model.date,
                                       state=model.state)


class ReplyMessageEntity(MessageEntity):
    __mapper_args__ = {'polymorphic_identity': 'reply'}

    reply_text: Mapped[str] = mapped_column(nullable=True)
    reply_to: Mapped[int] = mapped_column(nullable=True)

    def to_model(self) -> ReplyMessageModel:
        return ReplyMessageModel(id=self.id, user=self.user.to_model(), service_id=self.service_id,
                                 date=self.date,
                                 state=self.state,
                                 text=self.reply_text,
                                 reply_to=self.reply_to)

    @classmethod
    def from_model(cls, model: ReplyMessageModel) -> ReplyMessageEntity:
        return ReplyMessageEntity(reply_text=model.text,
                                  reply_to=model.reply_to,
                                  id=model.id,
                                  user_id=model.user.id,
                                  service_id=model.service_id,
                                  date=model.date,
                                  state=model.state)
