import abc
from datetime import datetime
from typing import Iterable

from adapter.spi.entity.session_entity import SessionEntity
from core.service import Service
from domain.model.session_model import Session
from domain.model.user_model import UserModel


class GetOpenSessionPort(abc.ABC):
    @abc.abstractmethod
    def get_open_user_sessions(self, user: UserModel, service: Service) -> Iterable[Session]:
        pass

    @abc.abstractmethod
    def get_open_sessions(self) -> Iterable[Session]:
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


class SessionChangedNotifierPort(abc.ABC):
    @abc.abstractmethod
    def notify_session_changed(self, session: Session):
        pass
