from typing import Iterable

from sqlalchemy import select

from adapter.spi.entity.user_entity import UserEntity
from db_connector import DBWorker
from domain.model.user_model import UserModel
from port.spi.user_port import FindUserPort, FindUserByChatIdPort, GetUserByIdPort, GetAllUsersPort


class DbUserRepository(FindUserPort, FindUserByChatIdPort, GetUserByIdPort, GetAllUsersPort):
    def find_user(self, user_id: str) -> UserModel:
        with DBWorker() as db:
            user_entity = db.scalar(select(UserEntity).where(UserEntity.external_id == user_id))

            return user_entity.to_model() if user_entity is not None else None

    def get_user_by_id(self, user_id: int) -> UserModel:
        with DBWorker() as db:
            user: UserEntity | None = db.get(UserEntity, user_id)
            return user.to_model() if user is not None else None

    def find_user_by_chat_id(self, chat_id: int):
        with DBWorker() as db:
            user_entity = db.scalar(select(UserEntity).where(UserEntity.tg_id == chat_id))

            if user_entity is None:
                user_entity = UserEntity(tg_id=chat_id)

                db.add(user_entity)
                db.commit()

            return user_entity.to_model()

    def get_all_users(self) -> Iterable[UserModel]:
        with DBWorker() as db:
            for u in db.scalars(select(UserEntity)):
                yield u.to_model()
