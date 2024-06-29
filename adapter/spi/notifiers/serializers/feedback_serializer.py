import enum

from domain.model.feedbacks import UserFeedbackVisitor, MessageUserFeedback, ReplyUserFeedback, ButtonUserFeedback


class FeedbackType(enum.Enum):
    BUTTON = 0
    MESSAGE = 1
    REPLY = 2


class FeedbackSerializer(UserFeedbackVisitor):
    def __init__(self):
        self.__feedback_data = {}

    def visit_button(self, entity: ButtonUserFeedback):
        self.__feedback_data = {
            "type": FeedbackType.BUTTON.name,
            "message_id": entity.message.id,
            "button_id": entity.button_id,
        }

    def visit_reply(self, entity: ReplyUserFeedback):
        self.__feedback_data = {
            "type": FeedbackType.REPLY.name,
            "message_id": entity.message.id,
            "text": entity.text
        }

    def visit_message(self, entity: MessageUserFeedback):
        self.__feedback_data = {
            "type": FeedbackType.MESSAGE.name,
            "message_id": entity.message.id,
            "text": entity.text
        }

    def extract(self):
        return self.__feedback_data
