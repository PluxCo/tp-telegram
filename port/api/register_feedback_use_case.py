from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(kw_only=True)
class RegisterFeedbackCommand(ABC):
    chat_id: int
    action_time: datetime


@dataclass(kw_only=True)
class RegisterMessageFeedbackCommand(RegisterFeedbackCommand):
    text: str


@dataclass(kw_only=True)
class RegisterReplyFeedbackCommand(RegisterMessageFeedbackCommand):
    message_id: int


@dataclass(kw_only=True)
class RegisterButtonFeedbackCommand(RegisterFeedbackCommand):
    message_id: int
    button_id: int


class RegisterFeedbackUseCase(ABC):
    @abstractmethod
    def register_message_feedback(self, command: RegisterMessageFeedbackCommand):
        pass

    @abstractmethod
    def register_reply_feedback(self, command: RegisterReplyFeedbackCommand):
        pass

    @abstractmethod
    def register_button_feedback(self, command: RegisterButtonFeedbackCommand):
        pass
