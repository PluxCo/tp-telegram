import abc
import datetime

from core.service import Service
from core.user import User


class SessionAggregator(abc.ABC):
    @abc.abstractmethod
    def initiate_sessions(self):
        pass


class InitSessionStrategy(abc.ABC):
    @abc.abstractmethod
    def selections_probability(self, user: User, service: Service, time: datetime.datetime) -> float:
        pass
