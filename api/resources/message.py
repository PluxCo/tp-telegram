import flask
from flask_restful import Resource, reqparse
from sqlalchemy import select

from api.parsers.feedback_parsers import FeedbackSerializer
from api.parsers.message_parsers import MessageCreator, StatusSerializer
from api.senders import ServiceFrame
from core.feedbacks import UserFeedback
from core.message import Message
from core.service import Service
from db_connector import DBWorker
from scenarios.routing_manager import simple_manager
from scenarios.scr import BaseFrame, ScenarioContext


class MessageResource(Resource):
    def post(self):
        args = flask.request.json

        parsed_messages = args["messages"]
        parsed_service_id = args["service_id"]

        with DBWorker() as db:
            service = db.get(Service, parsed_service_id)
            creator = MessageCreator(service)

            sent_messages = []

            for parsed_message in parsed_messages:
                message = creator.create_message(parsed_message, db)

                context = ScenarioContext(message.user, simple_manager)
                context.root_frames = [ServiceFrame(context, message)]
                context.start()

                sent_messages.append(StatusSerializer().dump_status(message))

        return {"sent_messages": sent_messages}, 200
