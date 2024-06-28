import abc

from domain.model.feedbacks import UserFeedback


class SaveFeedbackPort(abc.ABC):
    @abc.abstractmethod
    def save_feedback(self, feedback: UserFeedback) -> UserFeedback:
        pass
