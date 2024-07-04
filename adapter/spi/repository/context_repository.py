import logging
from typing import Optional

from domain.model.feedbacks import UserFeedback
from domain.model.message_model import MessageModel
from domain.service.scenarios import ScenarioContext, ScenarioSnapshot, Frame, ScenarioEventListener
from port.spi.context_provider_port import ScenarioContextLoaderPort, ContextFrameLinkerPort

logger = logging.getLogger(__name__)


class SimpleContextRepository(ContextFrameLinkerPort, ScenarioContextLoaderPort):
    def __init__(self):
        self.__alive_contexts: dict[int, ScenarioContext] = {}

        self.__snapshots: dict[int, ScenarioSnapshot] = {}

    def link_frame(self, message: MessageModel, frame: Frame, repair_state: bool = False):
        if repair_state:
            self.__snapshots[message.id] = frame.context.create_snapshot()

    def turn_to(self, frame: Frame, is_root=False):
        pass

    def load_context(self, feedback: UserFeedback) -> Optional[ScenarioContext]:
        context = self.__alive_contexts.get(feedback.user.id)

        if context is not None and feedback.message is not None and feedback.message.id in self.__snapshots:
            context.load_snapshot(self.__snapshots[feedback.message.id])

        logger.debug(f"Loaded hardcode context: {context}")

        return context

    def init_context(self, context: ScenarioContext):
        self.__alive_contexts[context.user.id] = context
