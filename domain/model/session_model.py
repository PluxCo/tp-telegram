import dataclasses
import datetime
import enum
from typing import Optional

from core.service import Service
from domain.model.user_model import UserModel


class SessionState(enum.Enum):
    OPEN = 1
    CLOSE = 2


@dataclasses.dataclass(kw_only=True)
class Session:
    id: Optional[int] = None

    user: UserModel
    service: Service
    state: SessionState = SessionState.OPEN

    open_time: datetime.datetime
    close_time: datetime.datetime = datetime.datetime.max

    def close(self):
        self.state = SessionState.CLOSE
        self.close_time = datetime.datetime.now()
