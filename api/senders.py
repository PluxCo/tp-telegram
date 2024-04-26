import enum
import logging

import requests
from sqlalchemy import select

from api.parsers.feedback_parsers import FeedbackSerializer
from api.parsers.session_parsers import SessionSerializer
from core.feedbacks import UserFeedback
from core.message import Message
from core.sessions.events import EventListener
from core.sessions.session import Session
from db_connector import DBWorker
from scenarios.scr import Frame, BaseFrame, ScenarioContext

logger = logging.getLogger(__name__)


class WebhhokEventType(enum.Enum):
    FEEDBACK = 1
    SESSION = 2


class ServiceFrame(BaseFrame):

    def __init__(self, context: ScenarioContext, message: Message):
        super().__init__(context)

        self.__message = message

    def exec(self):
        self.context.manager.link_frame(self.__message, self)

    def handle(self, feedback: UserFeedback):
        serializer = FeedbackSerializer()
        feedback.accept(serializer)

        feedback_data = serializer.extract()

        with DBWorker() as db:
            session = db.scalar(select(Session).where(feedback.message.date >= Session.open_time,
                                                      feedback.message.date <= Session.close_time,
                                                      Session.user_id == feedback.user.id,
                                                      Session.service_id == feedback.message.service_id))

        total_data = {
            "type": WebhhokEventType.FEEDBACK.name,
            "feedback": feedback_data,
            "session": SessionSerializer().dump(session) if session else None,
        }

        wh = feedback.message.service.webhook

        requests.post(wh, json=total_data)


class ApiSessionCreationNotifier(EventListener):
    def handle_event(self, sender: Session):
        session_data = SessionSerializer().dump(sender)

        total_data = {
            "type": WebhhokEventType.SESSION.name,
            "session": session_data
        }

        logger.debug(f"Sending session event: {session_data}")

        wh = sender.service.webhook
        requests.post(wh, json=total_data)
