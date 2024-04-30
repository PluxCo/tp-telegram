from dataclasses import dataclass

from port.api.register_feedback_use_case import RegisterFeedbackUseCase, RegisterButtonFeedbackCommand, \
    RegisterReplyFeedbackCommand, RegisterMessageFeedbackCommand
from port.spi.feedback_port import CreateFeedbackPort
from port.spi.user_port import FindUserByChatIdPort
from port.spi.message_port import GetMessageByInChatIdPort
from scenarios.routing_manager import RFM


@dataclass
class RegisterFeedbackService(RegisterFeedbackUseCase):
    __find_user_by_chat_id_port: FindUserByChatIdPort
    __get_message_by_in_chat_id_port: GetMessageByInChatIdPort
    __create_feedback_port: CreateFeedbackPort
    __manager: RFM

    def register_message_feedback(self, command: RegisterMessageFeedbackCommand):
        user = self.__find_user_by_chat_id_port.find_user_by_chat_id(command.chat_id)

        feedback = self.__create_feedback_port.create_message_feedback(command.text, user, command.action_time)

        self.__manager.handle(feedback)

    def register_reply_feedback(self, command: RegisterReplyFeedbackCommand):
        user = self.__find_user_by_chat_id_port.find_user_by_chat_id(command.chat_id)

        message = self.__get_message_by_in_chat_id_port.get_message_by_in_chat_id(command.message_id)

        feedback = self.__create_feedback_port.create_reply_feedback(command.text, user, command.action_time,
                                                                     message)

        self.__manager.handle(feedback)

    def register_button_feedback(self, command: RegisterButtonFeedbackCommand):
        user = self.__find_user_by_chat_id_port.find_user_by_chat_id(command.chat_id)

        message = self.__get_message_by_in_chat_id_port.get_message_by_in_chat_id(command.message_id)

        feedback = self.__create_feedback_port.create_button_feedback(user, command.action_time,
                                                                      message, command.button_id)

        self.__manager.handle(feedback)
