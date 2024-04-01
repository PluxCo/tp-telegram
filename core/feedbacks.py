from __future__ import annotations

import abc
from datetime import datetime

from core.message import Message
from core.user import User


class UserFeedback(abc.ABC):
    @abc.abstractmethod
    def accept(self, visitor: UserFeedbackVisitor):
        pass

    @abc.abstractmethod
    def source(self) -> Message:
        pass


class ButtonUserFeedback(UserFeedback):
    def __init__(self, message: Message, action_time: datetime, button_id: int):
        self.message = message
        self.action_time = action_time
        self.button_id = button_id

    def accept(self, visitor: UserFeedbackVisitor):
        visitor.visit_button(self)

    def source(self) -> Message:
        return self.message


class ReplyUserFeedback(UserFeedback):
    def __init__(self, message: Message, action_time: datetime, text: str):
        self.message = message
        self.action_time = action_time
        self.text = text

    def accept(self, visitor: UserFeedbackVisitor):
        visitor.visit_reply(self)

    def source(self) -> Message:
        return self.message


class MessageUserFeedback(UserFeedback):
    def __init__(self, text: str, action_time: datetime, user: User):
        self.action_time = action_time
        self.text = text
        self.user = user

        self.message = None

    def accept(self, visitor: UserFeedbackVisitor):
        visitor.visit_message(self)

    def source(self) -> Message:
        return self.message


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
