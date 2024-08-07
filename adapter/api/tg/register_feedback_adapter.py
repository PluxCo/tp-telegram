import logging
from datetime import datetime

from telebot import TeleBot
from telebot.types import Message, CallbackQuery

from port.api.register_feedback_use_case import RegisterReplyFeedbackCommand, RegisterMessageFeedbackCommand, \
    RegisterFeedbackUseCase, RegisterButtonFeedbackCommand

logger = logging.getLogger(__name__)

__register_feedback_use_case: RegisterFeedbackUseCase = ...
__bot: TeleBot = ...


def set_serivice(service: RegisterFeedbackUseCase, bot: TeleBot):
    global __register_feedback_use_case, __bot

    __register_feedback_use_case = service
    __bot = bot

    @__bot.message_handler()
    def main_handler(message: Message):
        logger.debug(f"Received message: {message}")

        if message.reply_to_message is not None:
            cmd = RegisterReplyFeedbackCommand(chat_id=message.from_user.id,
                                               action_time=datetime.now(),
                                               text=message.text,
                                               message_id=message.reply_to_message.id)

            __register_feedback_use_case.register_reply_feedback(cmd)
        else:
            cmd = RegisterMessageFeedbackCommand(chat_id=message.from_user.id,
                                                 action_time=datetime.now(),
                                                 text=message.text)

            __register_feedback_use_case.register_message_feedback(cmd)

    @__bot.callback_query_handler(func=lambda query: True)
    def btn_handler(callback_query: CallbackQuery):
        logger.debug(f"Pushed button: {callback_query}")
        __bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.id)

        _, message_id, button_id = callback_query.data.split("_")

        cmd = RegisterButtonFeedbackCommand(chat_id=callback_query.from_user.id,
                                            action_time=datetime.now(),
                                            message_id=callback_query.message.id,
                                            button_id=button_id)

        __register_feedback_use_case.register_button_feedback(cmd)
