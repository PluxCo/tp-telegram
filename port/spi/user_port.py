from abc import ABC, abstractmethod

from domain.model.user_model import UserModel


class FindUserPort(ABC):
    @abstractmethod
    def find_user(self, user_id: str) -> UserModel:
        pass


class FindUserByChatIdPort(ABC):
    @abstractmethod
    def find_user_by_chat_id(self, chat_id: int) -> UserModel:
        pass
