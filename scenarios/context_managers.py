import logging
from typing import Optional

from api.senders import ServiceFrame
from core.feedbacks import UserFeedback
from core.message import Message
from db_connector import DBWorker
from scenarios.scr import ScenarioContextManager, ScenarioContext, ScenarioSnapshot, Frame

logger = logging.getLogger(__name__)


class SimpleContextManager(ScenarioContextManager):
    def __init__(self):
        self.__alive_contexts: dict[int, ScenarioContext] = {}

        self.__snapshots: dict[int, ScenarioSnapshot] = {}

    def link_frame(self, message: Message, frame: Frame, repair_state: bool = False) -> int:
        with DBWorker() as db:
            message = db.merge(message)
            db.add(message)
            db.flush()

            if repair_state:
                self.__snapshots[message.id] = frame.context.create_snapshot()

            logger.debug(f"Sending message: {message}")
            message.send()
            db.commit()

            return message.id

    def turn_to(self, frame: Frame, is_root=False):
        pass

    def load_context(self, feedback: UserFeedback) -> Optional[ScenarioContext]:
        context = self.__alive_contexts.get(feedback.user.id)

        if context is None and feedback.message.service is not None:
            ctx = ScenarioContext(feedback.user, self)
            ctx.root_frames = [ServiceFrame(ctx, feedback.message)]
            ctx.change_state(execute=False)

            logger.debug(f"Loaded api context: {ctx}")

            return ctx

        if context is not None and feedback.message is not None and feedback.message.id in self.__snapshots:
            context.load_snapshot(self.__snapshots[feedback.message.id])

        logger.debug(f"Loaded hardcode context: {context}")

        return context

    def init_context(self, context: ScenarioContext):
        self.__alive_contexts[context.user.id] = context
