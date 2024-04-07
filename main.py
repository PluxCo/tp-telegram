import logging
from datetime import timedelta
from multiprocessing import Process
from threading import Thread

from tools import Settings
from db_connector import DBWorker

from api import app as api_app

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

bot_proc = Thread(target=bot.infinity_polling, daemon=True)
bot_proc.start()

api_app.run("0.0.0.0", port=3000, debug=False)
