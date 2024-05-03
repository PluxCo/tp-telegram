import logging
import os
from datetime import timedelta, time, datetime
from threading import Thread
from time import sleep
import alembic.config

from adapter.api.http.send_message_view import MessageView
from adapter.api.tg import register_feedback_adapter
from adapter.spi.repository.feedback_repositry import FeedbackRepository
from adapter.spi.repository.imgur_gif_finder import ImgurGifFinder
from adapter.spi.repository.message_repository import DbMessageRepository
from adapter.spi.repository.message_sender import TgMessageSender
from adapter.spi.repository.user_repository import DbUserRepository
from api.senders import ApiSessionCreationNotifier
from core.sessions.aggregation import SessionAggregator
from core.sessions.events import SessionEventManager, SessionEventType
from scenarios.routing_manager import session_manager, RFM
from service.message_service import MessageService
from service.register_feedback_service import RegisterFeedbackService
from tools import Settings
from db_connector import DBWorker

from api import app as api_app

from telegram.bot import bot

logging.basicConfig(level=logging.INFO)
logging.getLogger("telegram").setLevel(logging.DEBUG)
logging.getLogger("core").setLevel(logging.DEBUG)
logging.getLogger("scenarios").setLevel(logging.DEBUG)
logging.getLogger("planner").setLevel(logging.DEBUG)
logging.getLogger("api").setLevel(logging.DEBUG)
logging.getLogger("tools").setLevel(logging.DEBUG)

if __name__ == '__main__':
    alembic.config.main(['--raiseerr',
                         'upgrade', 'head'])

    DBWorker.init_db_file("sqlite:///data/database.db?check_same_thread=False")

    Settings.setup({
        "password": "32266",
        "amount_of_questions": 10,
        "session_duration": timedelta(minutes=10).total_seconds(),
        "start_time": time(0, 0).isoformat(),
        "end_time": time(23, 59).isoformat(),
        "period": timedelta(days=1).total_seconds(),
    })

    api_session_creation_notifier = ApiSessionCreationNotifier()
    session_event_manager = SessionEventManager()
    session_event_manager.subscribe(api_session_creation_notifier, SessionEventType.SESSION_CREATED)

    session_aggregator = SessionAggregator(session_event_manager)

# new
msg_rep = DbMessageRepository()
msg_sender = TgMessageSender()
usr_rep = DbUserRepository()
fb_rep = FeedbackRepository()
manager = RFM()

gif_finder = ImgurGifFinder(os.getenv("IMGUR_CLIENT_ID"))

message_service = MessageService(msg_rep, msg_rep, msg_sender, usr_rep, gif_finder)
feedback_service = RegisterFeedbackService(usr_rep, msg_sender, fb_rep, manager)

MessageView.set_service(message_service)
register_feedback_adapter.set_serivice(feedback_service)


    def schedule_poll():
        while True:
            try:
                sleep(5)
                curren_time = datetime.now()
                session_aggregator.initiate_sessions(curren_time)
            except Exception:
                logging.exception(f"Main schedule exception")


    session_manager.update_settings()

    logging.info("Starting polling")

    bot_th = Thread(target=bot.infinity_polling, daemon=True)
    bot_th.start()

    schedule_th = Thread(target=schedule_poll, daemon=True)
    schedule_th.start()

    api_app.run("0.0.0.0", port=os.getenv("PORT", 3000), debug=False)
