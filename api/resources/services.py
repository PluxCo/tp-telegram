import logging

import flask
from flask_restful import Resource
from sqlalchemy import select

from api.parsers.service_parsers import ServiceSerializer, ServiceCreator
from adapter.spi.entity.service_entity import ServiceEntity
from db_connector import DBWorker

logger = logging.getLogger(__name__)


class ServiceUnboundResource(Resource):
    def get(self):
        res = {
            "services": []
        }

        with DBWorker() as db:
            for s in db.scalars(select(ServiceEntity)):
                res["services"].append(ServiceSerializer().dump(s))

        return res, 200

    def post(self):
        service = ServiceCreator().create_service(flask.request.json)
        with DBWorker() as db:
            db.add(service)
            db.commit()

        return self.get()


class ServiceBoundResource(Resource):
    def delete(self, s_id):
        with DBWorker() as db:
            service = db.get(ServiceEntity, s_id)

            logger.debug(f"Deleting service {service}")
            db.delete(service)
            db.commit()

        return {}, 200
