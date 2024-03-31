import abc
import enum

from core.sessions.session import Session


class SessionEventType(enum.Enum):
    SESSION_CREATED = 1
    STATE_CHANGED = 2


class EventListener(abc.ABC):
    @abc.abstractmethod
    def handle_event(self, sender: Session):
        pass


class SessionEventManager:
    def __init__(self):
        self.__subscribers: list[tuple[EventListener, SessionEventType]] = []

    def subscribe(self, listener: EventListener, event_type: SessionEventType = None):
        self.__subscribers.append((listener, event_type))

    def notify(self, sender: Session, event_type: SessionEventType):
        for subscriber, e_type in self.__subscribers:
            if e_type == event_type:
                subscriber.handle_event(sender)
