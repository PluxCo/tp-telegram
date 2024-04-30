import abc
from datetime import datetime

from core.feedbacks import MessageUserFeedback, ReplyUserFeedback, ButtonUserFeedback

from domain.model.message_model import MessageModel
from domain.model.user_model import UserModel


class CreateFeedbackPort(abc.ABC):
    @abc.abstractmethod
    def create_message_feedback(self, text: str, user: UserModel, action_time: datetime) -> MessageUserFeedback:
        pass

    @abc.abstractmethod
    def create_reply_feedback(self, text: str, user: UserModel, action_time: datetime,
                              reply_to: MessageModel) -> ReplyUserFeedback:
        pass

    @abc.abstractmethod
    def create_button_feedback(self, user: UserModel, action_time: datetime,
                               message: MessageModel, button_id: int) -> ButtonUserFeedback:
        pass
