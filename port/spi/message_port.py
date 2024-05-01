from abc import ABC, abstractmethod

from domain.model.message_model import SimpleMessageModel, MessageModel, MessageWithButtonsModel, MotivationMessageModel
from domain.model.user_model import UserModel


class CreateMessagePort(ABC):
    @abstractmethod
    def create_simple_message(self, user: UserModel, service_id, text) -> SimpleMessageModel:
        pass

    @abstractmethod
    def create_message_with_buttons(self, user: UserModel, service_id, text, buttons) -> MessageWithButtonsModel:
        pass

    @abstractmethod
    def create_motivation_message(self, user: UserModel, service_id, mood) -> MotivationMessageModel:
        pass


class SaveMessagePort(ABC):
    @abstractmethod
    def save_simple_message(self, message: SimpleMessageModel):
        pass

    @abstractmethod
    def save_message_with_buttons(self, message: MessageWithButtonsModel):
        pass

    @abstractmethod
    def save_motivation_message(self, message: MotivationMessageModel):
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


class GetMessageByInChatIdPort(ABC):
    @abstractmethod
    def get_message_by_in_chat_id(self, message_id: int) -> MessageModel:
        pass
