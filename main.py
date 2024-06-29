import logging
import os
from datetime import timedelta, time, datetime
from threading import Thread
from time import sleep

import alembic.command
import telebot
from alembic.config import Config

from adapter.api.http.send_message_view import MessageView
from adapter.api.http.services_view import ServiceBoundView, ServiceUnboundView
from adapter.api.http.settings_view import SettingsView
from adapter.api.tg import register_feedback_adapter

from adapter.spi.notifiers.webhook_notifier import WebhookSessionNotifier
from adapter.spi.repository.context_repository import SimpleContextRepository
from adapter.spi.repository.feedback_repositry import FeedbackRepository
from adapter.spi.repository.imgur_gif_finder import ImgurGifFinder
from adapter.spi.repository.message_repository import DbMessageRepository
from adapter.spi.repository.message_sender import TgMessageSender
from adapter.spi.repository.service_repository import ServiceRepository
from adapter.spi.repository.session_repository import SessionRepository
from adapter.spi.repository.user_repository import DbUserRepository

from db_connector import DBWorker

from service.message_service import MessageService
from service.register_feedback_service import RegisterFeedbackService
from service.services_service import ServicesService
from service.session_aggregator import SessionAggregator
from service.settings_service import SettingsService

from tools import Settings
from urls import app as api_app

if __name__ == '__main__':
    config = Config('alembic.ini')

    alembic.command.upgrade(config, 'head')

    logging.basicConfig(level=logging.INFO)
    logging.getLogger("telegram").setLevel(logging.DEBUG)
    logging.getLogger("core").setLevel(logging.DEBUG)
    logging.getLogger("scenarios").setLevel(logging.DEBUG)
    logging.getLogger("planner").setLevel(logging.DEBUG)
    logging.getLogger("api").setLevel(logging.DEBUG)
    logging.getLogger("tools").setLevel(logging.DEBUG)
    logging.getLogger("adapter").setLevel(logging.DEBUG)
    logging.getLogger("service").setLevel(logging.DEBUG)
    logging.getLogger("domain").setLevel(logging.DEBUG)

    DBWorker.init_db_file("sqlite:///data/database.db?check_same_thread=False")

    stg = Settings()
    stg.setup({
        "password": "32266",
        "amount_of_questions": 10,
        "session_duration": timedelta(minutes=10).total_seconds(),
        "start_time": time(0, 0).isoformat(),
        "end_time": time(23, 59).isoformat(),
        "period": timedelta(days=1).total_seconds(),
    })

    telegram_bot = telebot.TeleBot(token=os.getenv("TG_TOKEN"))

    # new
    message_repo = DbMessageRepository()
    tg_message_sender = TgMessageSender(telegram_bot)
    user_repo = DbUserRepository()
    feedback_repo = FeedbackRepository()
    session_repo = SessionRepository()
    services_repo = ServiceRepository()

    gif_finder = ImgurGifFinder(os.getenv("IMGUR_CLIENT_ID"))

    wh_session_notifier = WebhookSessionNotifier()

    session_aggregator = SessionAggregator(session_repo, session_repo, user_repo, services_repo, wh_session_notifier,
                                           message_repo, timedelta(seconds=stg["period"]),
                                           time.fromisoformat(stg["start_time"]), time.fromisoformat(stg["end_time"]),
                                           stg["amount_of_questions"], timedelta(seconds=stg["session_duration"]))

    message_service = MessageService(message_repo, tg_message_sender, user_repo, gif_finder)

    context_manager = SimpleContextRepository(message_service)

    feedback_service = RegisterFeedbackService(user_repo, tg_message_sender, feedback_repo, wh_session_notifier,
                                               session_repo, session_aggregator, session_aggregator, context_manager)
    settings_service = SettingsService(session_aggregator)
    services_service = ServicesService(services_repo, services_repo, services_repo)

    MessageView.set_service(message_service)
    SettingsView.set_service(settings_service)
    ServiceBoundView.set_service(services_service)
    ServiceUnboundView.set_service(services_service)
    register_feedback_adapter.set_serivice(feedback_service, telegram_bot)


    def schedule_poll():
        while True:
            try:
                sleep(5)
                curren_time = datetime.now()
                session_aggregator.close_expired_session()
                session_aggregator.initiate_sessions(curren_time)
            except Exception:
                logging.exception(f"Main schedule exception")


    logging.info("Starting polling")

    bot_th = Thread(target=telegram_bot.infinity_polling, daemon=True)
    bot_th.start()

    schedule_th = Thread(target=schedule_poll, daemon=True)
    schedule_th.start()

    api_app.run("0.0.0.0", port=os.getenv("PORT", 3000), debug=False)
