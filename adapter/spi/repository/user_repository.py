import logging
import os
import uuid
from typing import Iterable

import requests
from sqlalchemy import select

from adapter.spi.entity.user_entity import UserEntity
from db_connector import DBWorker
from domain.model.user_model import UserModel
from port.spi.user_port import FindUserPort, FindUserByChatIdPort, GetUserByIdPort, GetAllUsersPort

logger = logging.getLogger(__name__)


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


class UserBuilder:
    def __init__(self, user_id: int):
        self.__user_id = user_id

        self.__name = None
        self.__groups: list[tuple] = []

        self.__fusion_token = os.getenv("FUSIONAUTH_TOKEN")
        self.__fusion_domain = os.getenv("FUSIONAUTH_DOMAIN")

    def available_groups(self) -> list[tuple[str, str]]:
        groups = requests.get(self.__fusion_domain + "/api/group",
                              headers={"Authorization": self.__fusion_token}).json()
        return [(g["id"], g["name"]) for g in groups["groups"]]

    def set_name(self, name: str):
        self.__name = name

    def add_group(self, group_id: str, level: int):
        self.__groups.append((group_id, level))

    def create_user(self):
        with DBWorker() as db:
            user = db.get(UserEntity, self.__user_id)
            user.name = self.__name

            person_info = {
                "user": {
                    "fullName": self.__name,
                    "username": str(uuid.uuid4()),
                    "password": str(uuid.uuid4()),
                    "memberships": [],
                    "data": {}
                }
            }

            person_info["user"]["data"]["groupLevels"] = []
            for g_id, g_level in self.__groups:
                person_info["user"]["memberships"].append({"groupId": g_id})

                person_info["user"]["data"]["groupLevels"].append({"groupId": g_id,
                                                                   "level": g_level})

            logger.debug(f"Creating user in fusionauth {person_info}")

            creation_resp = requests.post(self.__fusion_domain + "/api/user",
                                          headers={"Authorization": self.__fusion_token},
                                          json=person_info)

            creation_data = creation_resp.json()
            user.external_id = creation_data["user"]["id"]

            logger.debug(f"Committing user {user} with fusionauth {creation_data}")

            db.commit()

            return user.to_model()
