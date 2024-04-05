import logging
from datetime import timedelta

from tools import Settings
from db_connector import DBWorker

from telegram.bot import bot

logging.basicConfig(level=logging.INFO)
logging.getLogger("telegram").setLevel(logging.DEBUG)
logging.getLogger("core").setLevel(logging.DEBUG)
logging.getLogger("scenarios").setLevel(logging.DEBUG)

DBWorker.init_db_file("sqlite:///data/database.db")

Settings.setup({
    "password": "32266",
    "amount_of_questions": 10,
    "session_duration": timedelta(minutes=10).total_seconds()
})

logging.info("Starting polling")
bot.infinity_polling()
