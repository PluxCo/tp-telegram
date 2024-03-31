import abc

from core.feedbacks import UserFeedback
from core.message import Message


class FeedbackHandler(abc.ABC):
    @abc.abstractmethod
    def handle(self, feedback: UserFeedback):
        pass


class BaseInteraction(FeedbackHandler):
    def handle(self, feedback: UserFeedback):
        return

    def execute(self):
        return


class FeedbackManager(abc.ABC):
    @abc.abstractmethod
    def get_handler(self, feedback: UserFeedback) -> FeedbackHandler:
        pass

    @abc.abstractmethod
    def create_chain(self, root: FeedbackHandler, message: Message):
        pass
