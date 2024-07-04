from datetime import datetime

from domain.model.feedbacks import UserFeedback

from port.spi.feedback_port import SaveFeedbackPort


class FeedbackRepository(SaveFeedbackPort):
    def save_feedback(self, feedback: UserFeedback) -> UserFeedback:
        return feedback
