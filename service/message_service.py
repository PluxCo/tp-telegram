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

        message = self.__create_message_port.create_simple_message(user, command.service_id, command.text)

        self.__send_message_port.send_simple_message(message)
        message.send()

        self.__save_message_port.save_simple_message(message)

        return SendMessageResult(message.id, MessageStatus.SENT)

    def send_message_with_buttons(self, command: SendMessageWithButtonsCommand) -> SendMessageResult:
        user = self.__find_user_port.find_user(command.user_id)

        message = self.__create_message_port.create_message_with_buttons(user,
                                                                         command.service_id,
                                                                         command.text,
                                                                         command.buttons)

        self.__send_message_port.send_message_with_buttons(message)
        message.send()

        self.__save_message_port.save_message_with_buttons(message)

        return SendMessageResult(message.id, MessageStatus.SENT)

    def send_motivation_message(self, command: SendMotivationMessageCommand) -> SendMessageResult:
        user = self.__find_user_port.find_user(command.user_id)

        message = self.__create_message_port.create_motivation_message(user, command.service_id, command.mood)

        gif = self.__gif_finder_port.find_gif(command.mood)

        self.__send_message_port.send_motivation_message(message, gif)
        message.send()

        self.__save_message_port.save_motivation_message(message)

        return SendMessageResult(message.id, MessageStatus.SENT)

    def send_reply_message(self, command: SendReplyMessageCommand) -> SendMessageResult:
        user = self.__find_user_port.find_user(command.user_id)

        message = self.__create_message_port.create_reply_message(user,
                                                                  command.service_id,
                                                                  command.text,
                                                                  command.reply_to)

        self.__send_message_port.send_reply_message(message)
        message.send()

        self.__save_message_port.save_reply_message(message)

        return SendMessageResult(message.id, MessageStatus.SENT)
