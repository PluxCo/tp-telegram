from __future__ import annotations
import abc
from typing import Optional

from core.feedbacks import UserFeedback
from core.message import Message
from core.user import User


class FeedbackHandler(abc.ABC):
    @abc.abstractmethod
    def handle(self, feedback: UserFeedback):
        pass


class BaseInteraction(FeedbackHandler):
    def __init__(self, manager: FeedbackManager, user: User, next: Optional[BaseInteraction] = None):
        self._manager = manager
        self._user = user

        self._next: Optional[BaseInteraction] = next

    def set_next(self, next_inter: BaseInteraction):
        self._next = next_inter

    def handle(self, feedback: UserFeedback):
        if self._next is not None:
            self._next.execute()

    def execute(self):
        return


class FeedbackManager(abc.ABC):
    @abc.abstractmethod
    def get_handler(self, feedback: UserFeedback) -> FeedbackHandler:
        pass

    @abc.abstractmethod
    def create_chain(self, root: FeedbackHandler, message: Message):
        pass
