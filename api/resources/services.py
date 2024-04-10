import flask
from flask_restful import Resource, reqparse
from sqlalchemy import select

from api.parsers.service_parsers import ServiceSerializer, ServiceCreator
from core.service import Service
from db_connector import DBWorker
from tools import Settings


class ServiceUnboundResource(Resource):
    def get(self):
        res = {
            "services": []
        }

        with DBWorker() as db:
            for s in db.scalars(select(Service)):
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
            service = db.get(Service, s_id)
            db.delete(service)
            db.commit()

        return "", 200
