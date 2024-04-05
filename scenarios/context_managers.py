import logging

from core.feedbacks import UserFeedback
from core.message import Message
from db_connector import DBWorker
from scenarios.scr import ScenarioContextManager, ScenarioContext, ScenarioSnapshot, Frame

logger = logging.getLogger(__name__)


class SimpleContextManager(ScenarioContextManager):
    def __init__(self):
        self.__alive_contexts: dict[int, ScenarioContext] = {}

        self.__snapshots: dict[int, ScenarioSnapshot] = {}

    def link_frame(self, message: Message, frame: Frame):
        with DBWorker() as db:
            db.add(message)
            db.flush()

            self.__snapshots[message.id] = frame.context.create_snapshot()

            logger.debug(f"Sending message: {message}")
            message.send()
            db.commit()

    def turn_to(self, frame: Frame, is_root=False):
        pass

    def load_context(self, feedback: UserFeedback) -> ScenarioContext:
        context = self.__alive_contexts[feedback.user.id]

        if feedback.message is not None:
            context.load_snapshot(self.__snapshots[feedback.message.id])

        return context

    def init_context(self, context: ScenarioContext):
        self.__alive_contexts[context.user.id] = context
