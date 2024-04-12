import logging
import os
import uuid

import requests

from core.user import User
from db_connector import DBWorker

logger = logging.getLogger(__name__)


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
            user = db.get(User, self.__user_id)
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

            db.commit()
