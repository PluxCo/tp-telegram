from abc import ABC, abstractmethod
from typing import Iterable, Optional

from domain.model.user_model import UserModel


class FindUserPort(ABC):
    @abstractmethod
    def find_user(self, user_id: str) -> UserModel:
        pass


class GetUserByIdPort(ABC):
    @abstractmethod
    def get_user_by_id(self, user_id: int) -> UserModel:
        pass


class GetAllUsersPort(ABC):
    @abstractmethod
    def get_all_users(self) -> Iterable[UserModel]:
        pass


class FindUserByChatIdPort(ABC):
    @abstractmethod
    def find_user_by_chat_id(self, chat_id: int) -> UserModel:
        pass
