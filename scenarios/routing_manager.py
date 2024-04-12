from __future__ import annotations

import datetime
import logging

from sqlalchemy import select

from core.sessions.session import Session, SessionState
from db_connector import DBWorker
from planner.startegy_impl import SessionManager
from scenarios.context_managers import SimpleContextManager
from scenarios.frames import ConfirmStartFrame, PinConfirmationFrame, UserCreationFrame
from core.feedbacks import UserFeedback, UserFeedbackVisitor, ReplyUserFeedback, ButtonUserFeedback, MessageUserFeedback
from scenarios.scr import ScenarioContext

logger = logging.getLogger(__name__)

simple_manager = SimpleContextManager()
session_manager = SessionManager()


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
        self.__simple_manager = simple_manager

        self.selector = ScenariosSelector(self.__simple_manager)

    def handle(self, feedback: UserFeedback):
        with DBWorker() as db:
            sessions = db.scalars(select(Session).where(Session.user_id == feedback.user.id,
                                                        Session.state == SessionState.OPEN))

            for session in sessions:
                if session_manager.is_neccessary_to_close(session):
                    session.close()

            db.commit()

        feedback.accept(self.selector)

        context = self.__simple_manager.load_context(feedback)

        context.handle(feedback)
