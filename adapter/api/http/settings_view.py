import logging

import flask
from flask_restful import Resource

from port.api.settings_use_case import SettingsUseCase, ValueRequiredException, WrongTypeException

logger = logging.getLogger(__name__)


class SettingsView(Resource):
    __settings_use_case: SettingsUseCase

    @classmethod
    def set_service(cls, service: SettingsUseCase):
        cls.__settings_use_case = service

    def get(self):
        return self.__settings_use_case.get_settings(), 200

    def patch(self):
        args = flask.request.json

        try:
            self.__settings_use_case.set_settings(args)

            return self.__settings_use_case.get_settings(), 200
        except (ValueRequiredException, WrongTypeException) as e:
            logger.info("Failed to set settings: %s", str(e))
            return {"message": str(e)}, 400
