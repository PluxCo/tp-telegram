import logging

from domain.model.feedbacks import UserFeedback, ButtonUserFeedback, MessageUserFeedback, ReplyUserFeedback
from domain.model.message_model import SimpleMessageModel, MessageWithButtonsModel
from adapter.spi.repository.user_repository import UserBuilder
from domain.service.scenarios import BaseFrame, ScenarioContext

from tools import Settings

logger = logging.getLogger(__name__)


class ConfirmStartFrame(BaseFrame):
    def exec(self):
        message = MessageWithButtonsModel(text="Добро пожаловать в бота компании 3DiVi! Я здесь, чтобы "
                                               "помочь вам оценить и развить ваши профессиональные навыки. "
                                               "Пройдите тесты, получите обратную связь и станьте еще более "
                                               "квалифицированным специалистом. Начнем?\n(✿◠‿◠)",
                                          user=self.context.user, buttons=["Поехали!"])

        self.context.manager.link_frame(message, self)

    def handle(self, feedback: UserFeedback):
        if not isinstance(feedback, ButtonUserFeedback):
            return

        local_next = StartCreationFrame(self.context)

        self.context.change_state(local_next)


class StartCreationFrame(BaseFrame):
    def exec(self):
        message = SimpleMessageModel(text="Хорошо, давай начнем", user=self.context.user)

        self.context.manager.link_frame(message, self)
        self.context.change_state()


class PinConfirmationFrame(BaseFrame):
    def exec(self):
        message = SimpleMessageModel(text="Для продолжения необходимо ввести пароль.",
                                     user=self.context.user)

        self.context.manager.link_frame(message, self)

    def handle(self, feedback: UserFeedback):
        if not isinstance(feedback, (MessageUserFeedback, ReplyUserFeedback)):
            return

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
        message = SimpleMessageModel(text="Неверный пароль (ง ͠▧. ͡▧)ง",
                                     user=self.context.user)

        self.context.manager.link_frame(message, self.__master)  # Maybe not needed
        self.context.change_state(self.__master, execute=False)


class GoodPasswordFrame(BaseFrame):
    def exec(self):
        message = SimpleMessageModel(text="Отлично, можем продолжить (っ◔◡◔)っ❤",
                                     user=self.context.user)

        self.context.manager.link_frame(message, self)
        self.context.change_state()


class UserCreationFrame(BaseFrame):

    def __init__(self, context: ScenarioContext):
        super().__init__(context)

        self.__builder = UserBuilder(context.user.id)

    def exec(self):
        message = SimpleMessageModel(text="Как тебя зовут?",
                                     user=self.context.user)

        self.context.manager.link_frame(message, self)

    def handle(self, feedback: UserFeedback):
        if not isinstance(feedback, (MessageUserFeedback, ReplyUserFeedback)):
            return

        self.__builder.set_name(feedback.text)

        next_hop = GroupSelectionFrame(self.context, self.__builder)
        self.context.change_state(next_hop)


class GroupSelectionFrame(BaseFrame):
    def __init__(self, context: ScenarioContext, builder: UserBuilder):
        super().__init__(context)

        self.__builder = builder

    def exec(self):
        message = SimpleMessageModel(text="Выбери уровни групп, к которым ты относишься",
                                     user=self.context.user)

        self.context.manager.link_frame(message, self)

        self.context.change_state(GroupRowFrame(self.context, self.__builder))

    def handle(self, feedback: UserFeedback):
        pass


class GroupRowFrame(BaseFrame):
    def __init__(self, context: ScenarioContext, builder: UserBuilder):
        super().__init__(context)

        self.__builder = builder

        self.__groups = self.__builder.available_groups()
        self.__group_step = 0

    def exec(self):
        if self.__group_step >= len(self.__groups):
            self.context.change_state(UserCreationEndFrame(self.context, self.__builder))

            return

        message = MessageWithButtonsModel(text=self.__groups[self.__group_step][1],
                                          user=self.context.user, buttons=["Не отношусь", "1", "2", "3", "4", "5"])
        # Be accurate with buttons indices, bc levels selects by that.

        self.context.manager.link_frame(message, self)

    def handle(self, feedback: UserFeedback):
        if not isinstance(feedback, ButtonUserFeedback):
            return

        if feedback.button_id != 0:
            cur_group = self.__groups[self.__group_step]

            self.__builder.add_group(cur_group[0], feedback.button_id)

        self.__group_step += 1
        self.context.change_state(self)


class UserCreationEndFrame(BaseFrame):
    def __init__(self, context: ScenarioContext, builder: UserBuilder):
        super().__init__(context)

        self.__builder = builder

    def exec(self):
        user = self.__builder.create_user()

        message = SimpleMessageModel(text="Рады сообщить, что ты успешно зарегистрирован(а) в нашем боте. "
                                          "Добро пожаловать! 🚀",
                                     user=user)

        self.context.manager.link_frame(message, self)
        self.context.change_state()
