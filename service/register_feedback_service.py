import logging
from dataclasses import dataclass

from adapter.spi.repository.context_repository import SimpleContextRepository
from domain.model.feedbacks import UserFeedback, MessageUserFeedback, ButtonUserFeedback, ReplyUserFeedback
from domain.service.scenarios import ScenarioContext
from port.api.register_feedback_use_case import RegisterFeedbackUseCase, RegisterButtonFeedbackCommand, \
    RegisterReplyFeedbackCommand, RegisterMessageFeedbackCommand
from port.spi.feedback_port import SaveFeedbackPort, FeedbackRetrievedNotifierPort
from port.spi.message_port import GetMessageByInChatIdPort
from port.spi.session_port import CloseExpiredSessionPort, StartSessionPort, \
    GetSessionAtTimePort
from port.spi.user_port import FindUserByChatIdPort
from service.frames.register_frames import ConfirmStartFrame, PinConfirmationFrame, UserCreationFrame

logger = logging.getLogger(__name__)


@dataclass
class RegisterFeedbackService(RegisterFeedbackUseCase):
    __find_user_by_chat_id_port: FindUserByChatIdPort
    __get_message_by_in_chat_id_port: GetMessageByInChatIdPort

    __save_feedback_port: SaveFeedbackPort
    __feedback_retrieved_notifier_port: FeedbackRetrievedNotifierPort

    __get_session_at_time_port: GetSessionAtTimePort

    __close_expired_session_port: CloseExpiredSessionPort
    __start_session_port: StartSessionPort
    __context_repository: SimpleContextRepository

    def register_message_feedback(self, command: RegisterMessageFeedbackCommand):
        user = self.__find_user_by_chat_id_port.find_user_by_chat_id(command.chat_id)

        feedback = MessageUserFeedback(user, command.action_time, command.text)

        feedback = self.__save_feedback_port.save_feedback(feedback)

        self.__handle_feedback(feedback)

    def register_reply_feedback(self, command: RegisterReplyFeedbackCommand):
        message = self.__get_message_by_in_chat_id_port.get_message_by_in_chat_id(command.message_id)

        feedback = ReplyUserFeedback(message, command.action_time, command.text)

        feedback = self.__save_feedback_port.save_feedback(feedback)

        self.__handle_feedback(feedback)

    def register_button_feedback(self, command: RegisterButtonFeedbackCommand):
        message = self.__get_message_by_in_chat_id_port.get_message_by_in_chat_id(command.message_id)

        feedback = ButtonUserFeedback(message, command.action_time, command.button_id)

        feedback = self.__save_feedback_port.save_feedback(feedback)

        self.__handle_feedback(feedback)

    def __handle_feedback(self, feedback: UserFeedback):
        user = feedback.user

        self.__close_expired_session_port.close_expired_session(user)
        self.__start_session_port.start_user_session(user)

        self.__select_scenario(feedback)

        message = feedback.message

        if message.service_id is not None:
            session = self.__get_session_at_time_port.get_session_at_time(message.user, message.service_id,
                                                                          message.date)

            self.__feedback_retrieved_notifier_port.notify_feedback_retrieved(feedback, session)
            return

        ctx = self.__context_repository.load_context(feedback)

        if ctx is None:
            logger.warning(f"Failed to load context for: {feedback}")
            return

        ctx.handle(feedback)

    def __select_scenario(self, entity: UserFeedback):
        if isinstance(entity, MessageUserFeedback):
            if entity.text == "/start":
                context = ScenarioContext(entity.user, self.__context_repository)

                start = ConfirmStartFrame(context)
                pin = PinConfirmationFrame(context)
                user_creation = UserCreationFrame(context)

                context.root_frames = [start, pin, user_creation]

                self.__context_repository.init_context(context)

                logger.debug(f"Created context: {context}")
