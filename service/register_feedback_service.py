import logging
from dataclasses import dataclass

from core.feedbacks import UserFeedback, MessageUserFeedback
from domain.model.user_model import UserModel

from port.api.register_feedback_use_case import RegisterFeedbackUseCase, RegisterButtonFeedbackCommand, \
    RegisterReplyFeedbackCommand, RegisterMessageFeedbackCommand

from port.spi.feedback_port import CreateFeedbackPort
from port.spi.session_port import GetSessionByStatePort, SaveSessionPort, CloseExpiredSessionPort, StartSessionPort
from port.spi.user_port import FindUserByChatIdPort
from port.spi.message_port import GetMessageByInChatIdPort

from scenarios.context_managers import SimpleContextManager
from scenarios.frames import ConfirmStartFrame, PinConfirmationFrame, UserCreationFrame
from scenarios.scr import ScenarioContext

logger = logging.getLogger(__name__)


@dataclass
class RegisterFeedbackService(RegisterFeedbackUseCase):
    __find_user_by_chat_id_port: FindUserByChatIdPort
    __get_message_by_in_chat_id_port: GetMessageByInChatIdPort
    __create_feedback_port: CreateFeedbackPort

    __get_open_session_port: GetSessionByStatePort
    __save_session_port: SaveSessionPort

    __close_expired_session_port: CloseExpiredSessionPort
    __start_session_port: StartSessionPort
    __context_manager: SimpleContextManager

    def register_message_feedback(self, command: RegisterMessageFeedbackCommand):
        user = self.__find_user_by_chat_id_port.find_user_by_chat_id(command.chat_id)

        feedback = self.__create_feedback_port.create_message_feedback(command.text, user, command.action_time)

        self.__handle_feedback(feedback, user)

    def register_reply_feedback(self, command: RegisterReplyFeedbackCommand):
        user = self.__find_user_by_chat_id_port.find_user_by_chat_id(command.chat_id)

        message = self.__get_message_by_in_chat_id_port.get_message_by_in_chat_id(command.message_id)

        feedback = self.__create_feedback_port.create_reply_feedback(command.text, user, command.action_time,
                                                                     message)

        self.__handle_feedback(feedback, user)

    def register_button_feedback(self, command: RegisterButtonFeedbackCommand):
        user = self.__find_user_by_chat_id_port.find_user_by_chat_id(command.chat_id)

        message = self.__get_message_by_in_chat_id_port.get_message_by_in_chat_id(command.message_id)

        feedback = self.__create_feedback_port.create_button_feedback(user, command.action_time,
                                                                      message, command.button_id)

        self.__handle_feedback(feedback, user)

    # FIXME: remove user from signature when feedback will become domain model
    def __handle_feedback(self, feedback: UserFeedback, user: UserModel):
        self.__close_expired_session_port.close_expired_session(user)
        self.__start_session_port.start_user_session(user)

        self.__select_scenario(feedback)

        ctx = self.__context_manager.load_context(feedback)

        if ctx is None:
            logger.warning(f"Failed to load context for: {feedback}")
            return

        ctx.handle(feedback)

    def __select_scenario(self, entity: UserFeedback):
        if isinstance(entity, MessageUserFeedback):
            if entity.text == "/start":
                context = ScenarioContext(entity.user, self.__context_manager)

                start = ConfirmStartFrame(context)
                pin = PinConfirmationFrame(context)
                user_creation = UserCreationFrame(context)

                context.root_frames = [start, pin, user_creation]

                self.__context_manager.init_context(context)

                logger.debug(f"Created context: {context}")
