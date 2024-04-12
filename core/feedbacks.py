from __future__ import annotations

import abc
from datetime import datetime
from typing import Optional

from core.message import Message
from core.user import User


class UserFeedback(abc.ABC):

    @abc.abstractmethod
    def accept(self, visitor: UserFeedbackVisitor):
        pass

    @property
    @abc.abstractmethod
    def user(self) -> User:
        pass

    @property
    @abc.abstractmethod
    def message(self) -> Optional[Message]:
        pass


class ButtonUserFeedback(UserFeedback):
    def __init__(self, message: Message, action_time: datetime, button_id: int):
        self.__message = message
        self.action_time = action_time
        self.button_id = button_id

    def accept(self, visitor: UserFeedbackVisitor):
        visitor.visit_button(self)

    @property
    def user(self) -> User:
        return self.__message.user

    @property
    def message(self) -> Message:
        return self.__message


class ReplyUserFeedback(UserFeedback):
    def __init__(self, message: Message, action_time: datetime, text: str):
        self.__message = message
        self.action_time = action_time
        self.text = text

    def accept(self, visitor: UserFeedbackVisitor):
        visitor.visit_reply(self)

    @property
    def user(self) -> User:
        return self.__message.user

    @property
    def message(self) -> Message:
        return self.__message


class MessageUserFeedback(UserFeedback):
    def __init__(self, text: str, action_time: datetime, user: User):
        self.action_time = action_time
        self.text = text
        self.__user = user

    def accept(self, visitor: UserFeedbackVisitor):
        visitor.visit_message(self)

    @property
    def user(self) -> User:
        return self.__user

    @property
    def message(self) -> Optional[Message]:
        return None


class UserFeedbackVisitor(abc.ABC):
    @abc.abstractmethod
    def visit_button(self, entity: ButtonUserFeedback):
        pass

    @abc.abstractmethod
    def visit_reply(self, entity: ReplyUserFeedback):
        pass

    @abc.abstractmethod
    def visit_message(self, entity: MessageUserFeedback):
        pass
