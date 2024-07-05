from abc import ABC, abstractmethod
from datetime import datetime

from adapter.spi.entity.service_entity import ServiceEntity
from domain.model.message_model import SimpleMessageModel, MessageModel, MessageWithButtonsModel, \
    MotivationMessageModel, ReplyMessageModel
from domain.model.user_model import UserModel


class SaveMessagePort(ABC):
    @abstractmethod
    def save_message(self, message: MessageModel) -> MessageModel:
        pass


class SendMessagePort(ABC):
    @abstractmethod
    def send_simple_message(self, message: SimpleMessageModel):
        pass

    @abstractmethod
    def send_message_with_buttons(self, message: MessageWithButtonsModel):
        pass

    @abstractmethod
    def send_motivation_message(self, message: MotivationMessageModel, file_url: str):
        pass

    @abstractmethod
    def send_reply_message(self, message: ReplyMessageModel):
        pass


class GetMessageByInChatIdPort(ABC):
    @abstractmethod
    def get_message_by_in_chat_id(self, message_id: int) -> MessageModel:
        pass


class GetMessageInTimeIntervalPort(ABC):
    @abstractmethod
    def get_messages_count_in_time_interval(self, user: UserModel, service: ServiceEntity, begin: datetime,
                                            end: datetime) -> int:
        pass
