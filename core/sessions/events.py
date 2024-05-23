from __future__ import annotations

import abc
import enum
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adapter.spi.entity.session_entity import SessionEntity

logger = logging.getLogger(__name__)


class SessionEventType(enum.Enum):
    SESSION_CREATED = 1
    STATE_CHANGED = 2


class EventListener(abc.ABC):
    @abc.abstractmethod
    def handle_event(self, sender: SessionEntity):
        pass


class SessionEventManager:
    def __init__(self):
        self.__subscribers: list[tuple[EventListener, SessionEventType]] = []

    def subscribe(self, listener: EventListener, event_type: SessionEventType = None):
        self.__subscribers.append((listener, event_type))

    def notify(self, sender: SessionEntity, event_type: SessionEventType):
        logger.debug(f"Notifying session event {event_type} from {sender}")
        for subscriber, e_type in self.__subscribers:
            if e_type == event_type:
                subscriber.handle_event(sender)
