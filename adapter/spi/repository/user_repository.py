from sqlalchemy import select

from core.user import User
from db_connector import DBWorker
from domain.model.user_model import UserModel
from port.spi.user_port import FindUserPort, FindUserByChatIdPort


class DbUserRepository(FindUserPort, FindUserByChatIdPort):
    def find_user(self, user_id: str) -> UserModel:
        with DBWorker() as db:
            user_entity = db.scalar(select(User).where(User.external_id == user_id))

            return UserModel(user_entity.id)

    def find_user_by_chat_id(self, chat_id: int) -> UserModel:
        with DBWorker() as db:
            user_entity = db.scalar(select(User).where(User.tg_id == chat_id))

            return UserModel(user_entity.id)
