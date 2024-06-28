from typing import Optional

from domain.model.message_model import MessageModel, MessageVisitor, ReplyMessageModel, MotivationMessageModel, \
    MessageWithButtonsModel, SimpleMessageModel
from port.api.send_message_use_case import SendMessageUseCase, SendSimpleMessageCommand, SendMessageResult, \
    MessageStatus, SendMessageWithButtonsCommand, SendMotivationMessageCommand, SendReplyMessageCommand
from port.spi.gif_finder_port import GifFinderPort
from port.spi.message_port import CreateMessagePort, SendMessagePort, SaveMessagePort
from port.spi.user_port import FindUserPort


class MessageService(SendMessageUseCase):
    __create_message_port: CreateMessagePort
    __save_message_port: SaveMessagePort
    __send_message_port: SendMessagePort
    __find_user_port: FindUserPort

    __gif_finder_port: GifFinderPort

    def __init__(self, create_message_port: CreateMessagePort,
                 save_message_port: SaveMessagePort,
                 send_message_port: SendMessagePort,
                 find_user_port: FindUserPort,
                 gif_finder_port: GifFinderPort):
        self.__create_message_port = create_message_port
        self.__save_message_port = save_message_port
        self.__send_message_port = send_message_port
        self.__find_user_port = find_user_port

        self.__gif_finder_port = gif_finder_port

    def send_simple_message(self, command: SendSimpleMessageCommand) -> SendMessageResult:
        user = self.__find_user_port.find_user(command.user_id)

        if user is None:
            return SendMessageResult(-1, MessageStatus.CANCELED)

        message = self.__create_message_port.create_simple_message(user, command.service_id, command.text)

        return self.send_message(message)

    def send_message_with_buttons(self, command: SendMessageWithButtonsCommand) -> SendMessageResult:
        user = self.__find_user_port.find_user(command.user_id)

        if user is None:
            return SendMessageResult(-1, MessageStatus.CANCELED)

        message = self.__create_message_port.create_message_with_buttons(user,
                                                                         command.service_id,
                                                                         command.text,
                                                                         command.buttons)

        return self.send_message(message)

    def send_motivation_message(self, command: SendMotivationMessageCommand) -> SendMessageResult:
        user = self.__find_user_port.find_user(command.user_id)

        if user is None:
            return SendMessageResult(-1, MessageStatus.CANCELED)

        message = self.__create_message_port.create_motivation_message(user, command.service_id, command.mood)

        return self.send_message(message)

    def send_reply_message(self, command: SendReplyMessageCommand) -> SendMessageResult:
        user = self.__find_user_port.find_user(command.user_id)

        if user is None:
            return SendMessageResult(-1, MessageStatus.CANCELED)

        message = self.__create_message_port.create_reply_message(user,
                                                                  command.service_id,
                                                                  command.text,
                                                                  command.reply_to)

        return self.send_message(message)

    def send_message(self, message: MessageModel):
        message = self.__save_message_port.save_message(message)

        sender = _MessageComposer(self.__send_message_port, self.__save_message_port, self.__gif_finder_port)
        message.accept(sender)

        return sender.sending_result


class _MessageComposer(MessageVisitor):
    def __init__(self, send_message_port: SendMessagePort, save_message_port: SaveMessagePort,
                 gif_finder_port: GifFinderPort):
        self.__send_message_port = send_message_port
        self.__save_message_port = save_message_port
        self.__gif_finder_port = gif_finder_port

        self.sending_result: Optional[SendMessageResult] = None

    def visit_simple_message(self, message: SimpleMessageModel):
        self.__send_message_port.send_simple_message(message)
        message.send()

        self.__save_message_port.save_simple_message(message)

        self.sending_result = SendMessageResult(message.id, MessageStatus.SENT)

    def visit_message_with_buttons(self, message: MessageWithButtonsModel):
        self.__send_message_port.send_message_with_buttons(message)
        message.send()

        self.__save_message_port.save_message_with_buttons(message)

        self.sending_result = SendMessageResult(message.id, MessageStatus.SENT)

    def visit_motivation_message(self, message: MotivationMessageModel):
        gif = self.__gif_finder_port.find_gif(message.mood)

        self.__send_message_port.send_motivation_message(message, gif)
        message.send()

        self.__save_message_port.save_motivation_message(message)

        self.sending_result = SendMessageResult(message.id, MessageStatus.SENT)

    def visit_reply_message(self, message: ReplyMessageModel):
        self.__send_message_port.send_reply_message(message)
        message.send()

        self.__save_message_port.save_reply_message(message)

        self.sending_result = SendMessageResult(message.id, MessageStatus.SENT)
