from __future__ import annotations

import abc
from datetime import datetime

from core.message import Message


class UserFeedback(abc.ABC):
    @abc.abstractmethod
    def accept(self, visitor: UserFeedbackVisitor):
        pass


class ButonUserFeedback(UserFeedback):
    def __init__(self, message: Message, action_time: datetime, button_id: int):
        self.message = message
        self.action_time = action_time
        self.button_id = button_id

    def accept(self, visitor: UserFeedbackVisitor):
        visitor.visit_button(self)


class ReplyUserFeedback(UserFeedback):
    def __init__(self, message: Message, action_time: datetime, text: str):
        self.message = message
        self.action_time = action_time
        self.text = text

    def accept(self, visitor: UserFeedbackVisitor):
        visitor.visit_reply(self)


class UserFeedbackVisitor(abc.ABC):
    @abc.abstractmethod
    def visit_button(self, entity: ButonUserFeedback):
        pass

    @abc.abstractmethod
    def visit_reply(self, entity: ReplyUserFeedback):
        pass
