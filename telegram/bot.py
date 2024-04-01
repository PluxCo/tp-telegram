import os

import telebot

bot = telebot.TeleBot(token=os.getenv("TG_TOKEN"))
