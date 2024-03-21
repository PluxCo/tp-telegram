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
    "webhook": "https://7722bd2c-7def-4218-b9df-9b409b8cf34d.mock.pstmn.io/webhook"
}
# main_logger = setup_logger(__name__)
logging.basicConfig(level=logging.CRITICAL)

if __name__ == "__main__":
    # main_logger.info("initializing telegram service")
    Settings().setup("data/settings.json", default_settings)
    db_session.global_init("data/database.db")
    Schedule().from_settings().start()

    bot = bot.start_bot()
    app.run(debug=False, port=3000, host="0.0.0.0")
