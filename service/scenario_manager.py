import logging

from domain.model.feedbacks import UserFeedback, MessageUserFeedback
from domain.model.message_model import MessageModel as Message
from domain.service.scenarios import ScenarioEventListener, Frame, ScenarioContext
from port.spi.context_provider_port import ContextFrameLinkerPort, ScenarioContextLoaderPort
from service.frames.register_frames import ConfirmStartFrame, PinConfirmationFrame, UserCreationFrame

from service.message_service import MessageService
from service.register_feedback_service import FeedbackHandler

logger = logging.getLogger(__name__)


class ScenarioManager(ScenarioEventListener, FeedbackHandler):
    def __init__(self, context_linker_port: ContextFrameLinkerPort, context_loader_port: ScenarioContextLoaderPort,
                 message_service: MessageService):
        self.__context_linker = context_linker_port
        self.__context_loader = context_loader_port

        self.__message_service = message_service

    def message_attached(self, message: Message, frame: Frame, repair_state: bool = False) -> int:
        message_id = self.__message_service.send_message(message).message_id

        self.__context_linker.link_frame(message, frame, repair_state)

        return message_id

    def turn_to(self, frame: Frame, is_root=False):
        self.__context_linker.turn_to(frame, is_root)

    def handle(self, entity: UserFeedback):
        if isinstance(entity, MessageUserFeedback):
            if entity.text == "/start":
                context = ScenarioContext(entity.user, self)

                start = ConfirmStartFrame(context)
                pin = PinConfirmationFrame(context)
                user_creation = UserCreationFrame(context)

                context.root_frames = [start, pin, user_creation]

                self.__context_loader.init_context(context)

                logger.debug(f"Created context: {context}")

        ctx = self.__context_loader.load_context(entity)

        if ctx is None:
            logger.warning(f"Failed to load context for: {entity}")
            return

        ctx.handle(entity)
