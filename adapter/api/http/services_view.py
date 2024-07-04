import logging
import flask
from flask_restful import Resource

from port.api.service_use_case import ServiceUseCase

logger = logging.getLogger(__name__)


class ServiceUnboundView(Resource):
    __service_use_case: ServiceUseCase = ...

    @classmethod
    def set_service(cls, service: ServiceUseCase):
        cls.__service_use_case = service

    def get(self):
        res = {
            "services": self.__service_use_case.get_all_services()
        }

        return res, 200

    def post(self):
        data = flask.request.json

        self.__service_use_case.create_serivce(data["webhook"])

        return self.get()


class ServiceBoundView(Resource):
    __service_use_case: ServiceUseCase = ...

    @classmethod
    def set_service(cls, service: ServiceUseCase):
        cls.__service_use_case = service

    def delete(self, s_id):
        self.__service_use_case.delete_service(s_id)

        return {}, 200
