import enum

import requests

from api.parsers.feedback_parsers import FeedbackSerializer
from core.feedbacks import UserFeedback
from core.message import Message
from scenarios.scr import Frame, BaseFrame, ScenarioContext


class WebhhokEventType(enum.Enum):
    FEEDBACK = 1


class ServiceFrame(BaseFrame):

    def __init__(self, context: ScenarioContext, message: Message):
        super().__init__(context)

        self.__message = message

    def exec(self):
        self.context.manager.link_frame(self.__message, self)

    def handle(self, feedback: UserFeedback):
        serializer = FeedbackSerializer()
        feedback.accept(serializer)

        feedback_data = serializer.extract()

        total_data = {
            "type": WebhhokEventType.FEEDBACK.name,
            "feedback": feedback_data,
            "session": ""
        }

        wh = feedback.message.service.webhook

        requests.post(wh, json=total_data)
