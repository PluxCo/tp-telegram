import flask
from flask_restful import Resource, reqparse
from sqlalchemy import select

from api.parsers.message_parsers import MessageCreator
from core.service import Service
from db_connector import DBWorker


class MessageResource(Resource):
    def post(self):
        args = flask.request.json

        parsed_messages = args["messages"]
        parsed_service_id = args["service_id"]

        sent_messages = []

        with DBWorker() as db:
            service = db.get(Service, parsed_service_id)
            creator = MessageCreator(service)

            messages = []
            for m in parsed_messages:
                messages.append(creator.create_message(m, db))

            db.add_all(messages)
            db.flush()

            for current_message in messages:
                status = current_message.send()

                sent_messages.append({
                    "message_id": current_message.id,
                    "state": status.state.name
                })

            db.commit()

        return {"sent_messages": sent_messages}, 200
