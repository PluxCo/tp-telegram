import logging

from core.feedbacks import UserFeedback
from scenarios.scr import BaseFrame, ScenarioContext
from telegram.messages import MessageWithButtons, SimpleMessage
from tools import Settings

logger = logging.getLogger(__name__)


class ConfirmStartFrame(BaseFrame):
    def exec(self):
        message = MessageWithButtons(text="Добро пожаловать в бота компании 3DiVi! Я здесь, чтобы "
                                          "помочь вам оценить и развить ваши профессиональные навыки. "
                                          "Пройдите тесты, получите обратную связь и станьте еще более "
                                          "квалифицированным специалистом. Начнем?\n(✿◠‿◠) ",
                                     user=self.context.user, buttons=["Поехали!"])

        self.context.manager.link_frame(message, self)

    def handle(self, feedback: UserFeedback):
        local_next = StartCreationFrame(self.context)

        self.context.change_state(local_next)


class StartCreationFrame(BaseFrame):
    def exec(self):
        message = SimpleMessage(text="Хорошо, давай начнем", user=self.context.user)

        self.context.manager.link_frame(message, self)
        self.context.change_state()


class PinConfirmationFrame(BaseFrame):
    def exec(self):
        message = SimpleMessage(text="Для продолжения необходимо ввести пароль.",
                                user=self.context.user)

        self.context.manager.link_frame(message, self)

    def handle(self, feedback: UserFeedback):
        if feedback.text != Settings()["password"]:
            local_next = BadPasswordFrame(self.context, self)
            self.context.change_state(local_next)
        else:
            local_next = GoodPasswordFrame(self.context)
            self.context.change_state(local_next)


class BadPasswordFrame(BaseFrame):

    def __init__(self, context: ScenarioContext, master: PinConfirmationFrame):
        super().__init__(context)

        self.__master = master

    def exec(self):
        message = SimpleMessage(text="Неверный пароль (ง ͠▧. ͡▧)ง",
                                user=self.context.user)

        self.context.manager.link_frame(message, self.__master)  # Maybe not needed
        self.context.change_state(self.__master, execute=False)


class GoodPasswordFrame(BaseFrame):
    def exec(self):
        message = SimpleMessage(text="Отлично, можем продолжить (っ◔◡◔)っ ❤",
                                user=self.context.user)

        self.context.manager.link_frame(message, self)
        self.context.change_state()
