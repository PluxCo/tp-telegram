import enum
import logging
from typing import Optional

from sqlalchemy import select

from commands import ConfirmStart, BlankCommand, PinConfirmationCommand
from core.feedback_handler import FeedbackManager, FeedbackHandler, BaseInteraction
from core.feedbacks import UserFeedback, UserFeedbackVisitor, ReplyUserFeedback, ButtonUserFeedback, MessageUserFeedback
from core.message import Message
from db_connector import DBWorker

logger = logging.getLogger(__name__)


class FeedbackSelector(UserFeedbackVisitor):
    def __init__(self):
        self.__runtime_manager = RuntimeFeedbackManager()

        self.__handler: Optional[FeedbackHandler] = None

    def extract(self) -> FeedbackHandler:
        return self.__handler

    def visit_button(self, entity: ButtonUserFeedback):
        self.__handler = self.__runtime_manager.get_handler(entity)

    def visit_reply(self, entity: ReplyUserFeedback):
        pass

    def visit_message(self, entity: MessageUserFeedback):
        if entity.text == "/start":
            blank = BlankCommand(self.__runtime_manager, entity.user)
            start = ConfirmStart(self.__runtime_manager, entity.user)
            pin = PinConfirmationCommand(self.__runtime_manager, entity.user)
            blank.set_next(start)
            start.set_next(pin)

            self.__handler = blank
            return

        if entity.message is None:
            with DBWorker() as db:
                assigned_message = db.scalar(select(Message).
                                             where(Message.user_id == entity.user.id).
                                             order_by(Message.id.desc()))

                entity.message = assigned_message

        self.__handler = self.__runtime_manager.get_handler(entity)


class RuntimeFeedbackManager(FeedbackManager):

    def __init__(self):
        self.__commands: dict[int, FeedbackHandler] = {}

    def get_handler(self, feedback: UserFeedback) -> FeedbackHandler:
        return self.__commands[feedback.source().id]

    def create_chain(self, root: FeedbackHandler, message: Message):
        with DBWorker() as db:
            db.add(message)
            db.flush()

            self.__commands[message.id] = root

            message.send()

            db.commit()


class RFM:
    def __init__(self):
        self.selector = FeedbackSelector()

    def get_handler(self, feedback: UserFeedback) -> FeedbackHandler:
        feedback.accept(self.selector)
        return self.selector.extract()
