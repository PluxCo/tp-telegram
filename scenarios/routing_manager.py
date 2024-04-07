from __future__ import annotations

import logging

from scenarios.context_managers import SimpleContextManager
from scenarios.frames import ConfirmStartFrame, PinConfirmationFrame, UserCreationFrame
from core.feedbacks import UserFeedback, UserFeedbackVisitor, ReplyUserFeedback, ButtonUserFeedback, MessageUserFeedback
from scenarios.scr import ScenarioContext

logger = logging.getLogger(__name__)


class ScenariosSelector(UserFeedbackVisitor):
    def __init__(self, context_manager: SimpleContextManager):
        self.__context_manager = context_manager

    def visit_button(self, entity: ButtonUserFeedback):
        pass

    def visit_reply(self, entity: ReplyUserFeedback):
        pass

    def visit_message(self, entity: MessageUserFeedback):
        if entity.text == "/start":
            context = ScenarioContext(entity.user, self.__context_manager)

            start = ConfirmStartFrame(context)
            pin = PinConfirmationFrame(context)
            user_creation = UserCreationFrame(context)

            context.root_frames = [start, pin, user_creation]

            self.__context_manager.init_context(context)

            logger.debug(f"Created context: {context}")


class RFM:
    def __init__(self):
        self.__context_manager = SimpleContextManager()

        self.selector = ScenariosSelector(self.__context_manager)

    def handle(self, feedback: UserFeedback):
        feedback.accept(self.selector)

        context = self.__context_manager.load_context(feedback)

        logger.debug(f"Loaded context: {context}")

        context.handle(feedback)
