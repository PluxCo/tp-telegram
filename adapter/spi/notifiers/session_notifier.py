import logging

import requests

from api.senders import WebhhokEventType
from domain.model.session_model import Session
from port.spi.session_port import SessionChangedNotifierPort

logger = logging.getLogger(__name__)


class WebhookSessionNotifier(SessionChangedNotifierPort):
    def notify_session_changed(self, session: Session):
        session_data = self.__dump_session_data(session)

        total_data = {
            "type": WebhhokEventType.SESSION.name,
            "session": session_data
        }

        logger.debug(f"Sending session event: {session_data}")

        wh = session.service.webhook
        requests.post(wh, json=total_data)

    def __dump_session_data(self, session: Session):
        data = {
            "user_id": session.user.external_id,
            "state": session.state.name
        }

        return data
