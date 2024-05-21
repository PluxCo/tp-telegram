from typing import Iterable

from sqlalchemy import select

from core.user import User
from db_connector import DBWorker
from domain.model.user_model import UserModel
from port.spi.user_port import FindUserPort, FindUserByChatIdPort, GetUserByIdPort, GetAllUsersPort


class DbUserRepository(FindUserPort, FindUserByChatIdPort, GetUserByIdPort, GetAllUsersPort):
    def find_user(self, user_id: str) -> UserModel:
        with DBWorker() as db:
            user_entity = db.scalar(select(User).where(User.external_id == user_id))

            return user_entity.to_model() if user_entity is not None else None

    def get_user_by_id(self, user_id: int) -> UserModel:
        with DBWorker() as db:
            user: User | None = db.get(User, user_id)
            return user.to_model() if user is not None else None

    def find_user_by_chat_id(self, chat_id: int) -> UserModel:
        with DBWorker() as db:
            user_entity = db.scalar(select(User).where(User.tg_id == chat_id))

            return user_entity.to_model()

    def get_all_users(self) -> Iterable[UserModel]:
        with DBWorker() as db:
            for u in db.scalars(select(User)):
                yield u.to_model()
