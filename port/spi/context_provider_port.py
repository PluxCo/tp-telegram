from __future__ import annotations

import abc
from typing import Optional, TYPE_CHECKING

from domain.model.feedbacks import UserFeedback
from domain.model.message_model import MessageModel

if TYPE_CHECKING:
    from domain.service.scenarios import ScenarioContext, Frame


class ScenarioContextLoaderPort(abc.ABC):
    @abc.abstractmethod
    def load_context(self, feedback: UserFeedback) -> Optional[ScenarioContext]:
        pass

    @abc.abstractmethod
    def init_context(self, context: ScenarioContext):
        pass


class ContextFrameLinkerPort(abc.ABC):
    @abc.abstractmethod
    def link_frame(self, message: MessageModel, frame: Frame, repair_state: bool = False):
        pass

    @abc.abstractmethod
    def turn_to(self, frame: Frame, is_root=False):
        pass
