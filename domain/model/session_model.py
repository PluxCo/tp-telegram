import dataclasses
import datetime
import enum
from typing import Optional

from adapter.spi.entity.service_entity import ServiceEntity
from domain.model.user_model import UserModel


class SessionState(enum.Enum):
    OPEN = 1
    STARTED = 3
    CLOSE = 2


@dataclasses.dataclass(kw_only=True)
class Session:
    id: Optional[int] = None

    user: UserModel
    service: ServiceEntity
    state: SessionState = SessionState.OPEN

    open_time: datetime.datetime
    start_time: datetime.datetime = None
    close_time: datetime.datetime = datetime.datetime.max

    def start(self):
        self.state = SessionState.STARTED
        self.start_time = datetime.datetime.now()

    def close(self):
        self.state = SessionState.CLOSE
        self.close_time = datetime.datetime.now()
