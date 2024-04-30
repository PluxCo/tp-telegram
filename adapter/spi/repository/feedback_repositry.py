from datetime import datetime

from core.feedbacks import ButtonUserFeedback, ReplyUserFeedback, MessageUserFeedback
from core.message import Message
from core.user import User
from db_connector import DBWorker
from domain.model.message_model import MessageModel
from domain.model.user_model import UserModel
from port.spi.feedback_port import CreateFeedbackPort


class FeedbackRepository(CreateFeedbackPort):
    def create_message_feedback(self, text: str, user: UserModel, action_time: datetime) -> MessageUserFeedback:
        with DBWorker() as db:
            user_entity = db.get(User, user.id)
            return MessageUserFeedback(text, action_time, user_entity)

    def create_reply_feedback(self, text: str, user: UserModel, action_time: datetime,
                              reply_to: MessageModel) -> ReplyUserFeedback:
        with DBWorker() as db:
            message = db.get(Message, reply_to.id)
            return ReplyUserFeedback(message, action_time, text)

    def create_button_feedback(self, user: UserModel, action_time: datetime, message: MessageModel,
                               button_id: int) -> ButtonUserFeedback:
        with DBWorker() as db:
            message = db.get(Message, message.id)
            return ButtonUserFeedback(message, action_time, button_id)
