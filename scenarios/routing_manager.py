from __future__ import annotations

import logging

from scenarios.frames import ConfirmStartFrame, PinConfirmationFrame
from core.feedbacks import UserFeedback, UserFeedbackVisitor, ReplyUserFeedback, ButtonUserFeedback, MessageUserFeedback
from core.message import Message
from db_connector import DBWorker
from scenarios.scr import ScenarioContextManager, Frame, ScenarioContext, ScenarioSnapshot

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

            context.root_frames = [start, pin]

            self.__context_manager.init_context(context)

            logger.debug(f"Created context: {context}")


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


class RFM:
    def __init__(self):
        self.__context_manager = SimpleContextManager()

        self.selector = ScenariosSelector(self.__context_manager)

    def handle(self, feedback: UserFeedback):
        feedback.accept(self.selector)

        context = self.__context_manager.load_context(feedback)
        logger.debug(f"Loaded context: {context}")

        context.handle(feedback)
