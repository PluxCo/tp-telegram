import enum
import logging

import requests

from adapter.spi.notifiers.serializers.feedback_serializer import FeedbackSerializer

from domain.model.feedbacks import UserFeedback
from domain.model.session_model import Session, SessionState
from port.spi.session_port import SessionChangedNotifierPort
from port.spi.feedback_port import FeedbackRetrievedNotifierPort

logger = logging.getLogger(__name__)


class WebhhokEventType(enum.Enum):
    FEEDBACK = 1
    SESSION = 2


class WebhookSessionNotifier(SessionChangedNotifierPort, FeedbackRetrievedNotifierPort):
    def notify_session_changed(self, session: Session):
        session_data = self.__dump_session_data(session)

        total_data = {
            "type": WebhhokEventType.SESSION.name,
            "session": session_data
        }

        logger.debug(f"Sending session event: {session_data}")

        wh = session.service.webhook
        requests.post(wh, json=total_data)

    def notify_feedback_retrieved(self, feedback: UserFeedback, session: Session):
        serializer = FeedbackSerializer()
        feedback.accept(serializer)

        feedback_data = serializer.extract()

        total_data = {
            "type": WebhhokEventType.FEEDBACK.name,
            "feedback": feedback_data,
            "session": self.__dump_session_data(session)
        }

        logger.debug(f"Sending feedback event: {total_data}")

        wh = session.service.webhook
        requests.post(wh, json=total_data)

    def __dump_session_data(self, session: Session):
        data = {
            "user_id": session.user.external_id,
            "state": "OPEN" if session.state in (SessionState.OPEN, SessionState.STARTED) else "CLOSE"
        }

        return data
