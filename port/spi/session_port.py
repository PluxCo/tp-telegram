import abc
from datetime import datetime
from typing import Iterable, Optional

from domain.model.service_model import ServiceModel
from domain.model.session_model import Session, SessionState
from domain.model.user_model import UserModel


class GetSessionByStatePort(abc.ABC):
    @abc.abstractmethod
    def get_user_sessions(self, user: Optional[UserModel], service: Optional[ServiceModel],
                          states: list[SessionState]) -> Iterable[Session]:
        pass


class SaveSessionPort(abc.ABC):
    @abc.abstractmethod
    def save_session(self, session: Session):
        pass


class CloseExpiredSessionPort(abc.ABC):
    @abc.abstractmethod
    def close_expired_session(self, user: UserModel = None):
        pass


class InitSessionPort(abc.ABC):
    @abc.abstractmethod
    def initiate_sessions(self, pick_time: datetime):
        pass


class StartSessionPort(abc.ABC):
    @abc.abstractmethod
    def start_user_session(self, user: UserModel):
        pass


class SessionChangedNotifierPort(abc.ABC):
    @abc.abstractmethod
    def notify_session_changed(self, session: Session):
        pass
