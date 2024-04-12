from __future__ import annotations
import abc
from typing import Optional

from core.feedbacks import UserFeedback
from core.message import Message
from core.user import User


class Frame(abc.ABC):
    @abc.abstractmethod
    def handle(self, feedback: UserFeedback):
        """Calls when :meth:`ScenarioContext.handle` is called"""
        pass

    @abc.abstractmethod
    def exec(self):
        """Method that calls from :class:`ScenarioContext` when state changed to that"""
        pass

    @property
    @abc.abstractmethod
    def context(self) -> ScenarioContext:
        pass


class ScenarioContextManager(abc.ABC):
    @abc.abstractmethod
    def link_frame(self, message: Message, frame: Frame, repair_state: bool = False) -> int:
        pass

    @abc.abstractmethod
    def turn_to(self, frame: Frame, is_root=False):
        pass


class ScenarioSnapshot:
    def __init__(self, current_frame: Frame, current_root_idx: int):
        self.current_frame = current_frame
        self.current_root_idx = current_root_idx


class ScenarioContext:
    # Внебрачный сын тайской шлюхи (машины состояний, команды, цепочки обязанностей, наблюдателя и снапшота).
    def __init__(self, user: User, context_manager: ScenarioContextManager, start: Frame = None):
        self.__user = user
        self.__context_manager = context_manager

        self.__frame = BaseFrame(self) if start is None else start

        self.root_frames = []
        self.__current_root_idx = 0

    @property
    def user(self) -> User:
        return self.__user

    @property
    def manager(self) -> ScenarioContextManager:
        return self.__context_manager

    def handle(self, feedback: UserFeedback):
        self.__frame.handle(feedback)

    def start(self):
        self.__frame.exec()

    def change_state(self, next_frame: Optional[Frame] = None, execute: bool = True):
        """Switch to next_frame. If that not given then takes it from root_frames_queue"""
        self.__frame = next_frame
        is_root_frame = False

        if self.__frame is None and self.__current_root_idx < len(self.root_frames):
            self.__frame = self.root_frames[self.__current_root_idx]
            self.__current_root_idx += 1
            is_root_frame = True

        self.manager.turn_to(self.__frame, is_root=is_root_frame)

        if self.__frame is not None and execute:
            self.__frame.exec()

    def create_snapshot(self) -> ScenarioSnapshot:
        return ScenarioSnapshot(self.__frame, self.__current_root_idx)

    def load_snapshot(self, snapshot: ScenarioSnapshot):
        self.__frame = snapshot.current_frame
        self.__current_root_idx = snapshot.current_root_idx


class BaseFrame(Frame):
    def __init__(self, context: ScenarioContext):
        self.__context = context

    @property
    def context(self) -> ScenarioContext:
        return self.__context

    def handle(self, feedback: UserFeedback):
        self.context.change_state()

    def exec(self):
        self.context.change_state()
