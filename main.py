import logging
from datetime import timedelta, time, datetime
from threading import Thread
from time import sleep

from api.senders import ApiSessionCreationNotifier
from core.sessions.aggregation import SessionAggregator
from core.sessions.events import SessionEventManager, SessionEventType
from planner.startegy_impl import SimpleWindowSessionStrategy
from scenarios.routing_manager import session_manager
from tools import Settings
from db_connector import DBWorker

from api import app as api_app

from telegram.bot import bot

logging.basicConfig(level=logging.INFO)
logging.getLogger("telegram").setLevel(logging.DEBUG)
logging.getLogger("core").setLevel(logging.DEBUG)
logging.getLogger("scenarios").setLevel(logging.DEBUG)
logging.getLogger("planner").setLevel(logging.DEBUG)

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

session_strategy = SimpleWindowSessionStrategy()

session_aggregator = SessionAggregator(session_strategy, session_event_manager)


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

api_app.run("0.0.0.0", port=3000, debug=False)
