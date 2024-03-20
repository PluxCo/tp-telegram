import datetime
import logging

from api.telegram_api import app
from bot import bot
from models import db_session
from tools import Settings

from schedule.schedule import Schedule

default_settings = {
    "pin": "32266",
    "amount_of_questions": 10,
    "session_duration": datetime.timedelta(minutes=10).total_seconds(),
    "time_period": datetime.timedelta(seconds=30),
    "from_time": datetime.time(0),
    "to_time": datetime.time(23, 59),
    "week_days": [d for d in range(7)],
    "webhook": ""
}
# main_logger = setup_logger(__name__)
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    # main_logger.info("initializing telegram service")
    Settings().setup("data/settings.json", default_settings)
    db_session.global_init("data/database.db")
    # sch = Schedule()
    bot = bot.start_bot()
    app.run(debug=False, port=3000, host="0.0.0.0")
