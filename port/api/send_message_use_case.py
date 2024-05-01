import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(kw_only=True)
class SendMessageCommand:
    user_id: str
    service_id: int = None


@dataclass(kw_only=True)
class SendSimpleMessageCommand(SendMessageCommand):
    text: str


@dataclass(kw_only=True)
class SendMessageWithButtonsCommand(SendMessageCommand):
    text: str
    buttons: list[str]


@dataclass(kw_only=True)
class SendMotivationMessageCommand(SendMessageCommand):
    mood: str


class MessageStatus(enum.Enum):
    SENT = 0
    PENDING = 1
    CANCELED = 2


@dataclass
class SendMessageResult:
    message_id: int
    status: MessageStatus


class SendMessageUseCase(ABC):
    @abstractmethod
    def send_simple_message(self, command: SendSimpleMessageCommand) -> SendMessageResult:
        pass

    @abstractmethod
    def send_message_with_buttons(self, command: SendMessageWithButtonsCommand) -> SendMessageResult:
        pass

    @abstractmethod
    def send_motivation_message(self, command: SendMotivationMessageCommand) -> SendMessageResult:
        pass
