import logging
from typing import Optional

from api.senders import ServiceFrame
from domain.model.feedbacks import UserFeedback
from domain.model.message_model import MessageModel as Message
from db_connector import DBWorker
from scenarios.scr import ScenarioContextManager, ScenarioContext, ScenarioSnapshot, Frame
from service.message_service import MessageService

logger = logging.getLogger(__name__)


class SimpleContextManager(ScenarioContextManager):
    def __init__(self, message_service: MessageService):
        self.__message_service = message_service

        self.__alive_contexts: dict[int, ScenarioContext] = {}

        self.__snapshots: dict[int, ScenarioSnapshot] = {}

    def link_frame(self, message: Message, frame: Frame, repair_state: bool = False) -> int:
        with DBWorker() as db:
            if repair_state:
                self.__snapshots[message.id] = frame.context.create_snapshot()

            res = self.__message_service.send_message(message)

            return res.message_id

    def turn_to(self, frame: Frame, is_root=False):
        pass

    def load_context(self, feedback: UserFeedback) -> Optional[ScenarioContext]:
        context = self.__alive_contexts.get(feedback.user.id)

        if feedback.message is not None and feedback.message.service_id is not None:
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
