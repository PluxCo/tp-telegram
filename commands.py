import logging
from typing import Optional

from core.feedback_handler import BaseInteraction, FeedbackManager
from core.feedbacks import UserFeedback
from core.user import User
from db_connector import DBWorker
from telegram.messages import SimpleMessage, MessageWithButtons
from tools import Settings

logger = logging.getLogger(__name__)


class BlankCommand(BaseInteraction):
    pass


class ConfirmStart(BaseInteraction):
    def execute(self):
        message = MessageWithButtons(text="Добро пожаловать в бота компании 3DiVi! Я здесь, чтобы "
                                          "помочь вам оценить и развить ваши профессиональные навыки. "
                                          "Пройдите тесты, получите обратную связь и станьте еще более "
                                          "квалифицированным специалистом. Начнем?\n(✿◠‿◠) ",
                                     user=self._user, buttons=["Поехали!"])

        self._manager.create_chain(self, message)

    def handle(self, feedback: UserFeedback):
        local_next = StartCreationCommand(self._manager, self._user, self._next)
        local_next.execute()

        super().handle(feedback)


class StartCreationCommand(BaseInteraction):
    def execute(self):
        message = SimpleMessage(text="Хорошо, давай начнем", user=self._user)

        self._manager.create_chain(self, message)


class PinConfirmationCommand(BaseInteraction):
    def execute(self):
        message = SimpleMessage(text="Для продолжения необходимо ввести пароль.",
                                user=self._user)

        self._manager.create_chain(self, message)

    def handle(self, feedback: UserFeedback):
        if feedback.text != Settings()["password"]:
            local_next = BadPasswordCommand(self, self._manager, self._user)
            local_next.execute()
        else:
            local_next = GoodPasswordCommand(self._manager, self._user, self._next)
            local_next.execute()

            super().handle(feedback)


class BadPasswordCommand(BaseInteraction):
    def __init__(self, master: PinConfirmationCommand, manager: FeedbackManager, user: User,
                 next: Optional[BaseInteraction] = None):
        super().__init__(manager, user, next)
        self.__master = master

    def execute(self):
        message = SimpleMessage(text="Неверный пароль (ง ͠▧. ͡▧)ง",
                                user=self._user)

        self._manager.create_chain(self.__master, message)


class GoodPasswordCommand(BaseInteraction):
    def execute(self):
        message = SimpleMessage(text="Отлично, можем продолжить (っ◔◡◔)っ ❤",
                                user=self._user)

        self._manager.create_chain(self, message)
