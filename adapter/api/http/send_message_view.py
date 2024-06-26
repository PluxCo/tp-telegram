import logging

import flask
from flask_restful import Resource

from port.api.send_message_use_case import SendMessageUseCase, SendSimpleMessageCommand, SendMessageResult, \
    SendMessageWithButtonsCommand, SendMotivationMessageCommand, SendReplyMessageCommand

logger = logging.getLogger(__name__)


class MessageView(Resource):
    _send_message_use_case: SendMessageUseCase

    @classmethod
    def set_service(cls, service: SendMessageUseCase):
        cls._send_message_use_case = service

    def post(self):
        args = flask.request.json

        parsed_messages = args["messages"]
        parsed_service_id = args["service_id"]

        sent_messages = []

        for parsed_message in parsed_messages:
            logger.info(f"Sending: {parsed_message}")
            res = None
            match parsed_message["type"]:
                case "SIMPLE":
                    res = self._send_message_use_case.send_simple_message(
                        self.__read_command(parsed_message, parsed_service_id)
                    )
                case "WITH_BUTTONS":
                    res = self._send_message_use_case.send_message_with_buttons(
                        self.__read_command(parsed_message, parsed_service_id)
                    )
                case "MOTIVATION":
                    res = self._send_message_use_case.send_motivation_message(
                        self.__read_command(parsed_message, parsed_service_id)
                    )
                case "REPLY":
                    res = self._send_message_use_case.send_reply_message(
                        self.__read_command(parsed_message, parsed_service_id)
                    )

            sent_messages.append(self.__build_response(res))

        return {"sent_messages": sent_messages}, 200

    def __read_command(self, data: dict, service_id: int):
        match data["type"]:
            case "SIMPLE":
                return SendSimpleMessageCommand(user_id=data["user_id"],
                                                service_id=service_id,
                                                text=data["text"])
            case "WITH_BUTTONS":
                return SendMessageWithButtonsCommand(user_id=data["user_id"],
                                                     service_id=service_id,
                                                     text=data["text"],
                                                     buttons=data["buttons"])
            case "MOTIVATION":
                return SendMotivationMessageCommand(user_id=data["user_id"],
                                                    service_id=service_id,
                                                    mood=data["mood"])
            case "REPLY":
                return SendReplyMessageCommand(user_id=data["user_id"],
                                               service_id=service_id,
                                               text=data["text"],
                                               reply_to=data["reply_to"])

    def __build_response(self, res: SendMessageResult):
        return {"message_id": res.message_id, "status": res.status.name}
