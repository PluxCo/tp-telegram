import abc

from domain.model.feedbacks import UserFeedback
from domain.model.session_model import Session


class SaveFeedbackPort(abc.ABC):
    @abc.abstractmethod
    def save_feedback(self, feedback: UserFeedback) -> UserFeedback:
        pass


class FeedbackRetrievedNotifierPort(abc.ABC):
    @abc.abstractmethod
    def notify_feedback_retrieved(self, feedback: UserFeedback, session: Session):
        pass
