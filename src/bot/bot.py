import sys
import telebot
from pathlib import Path

import os

src_path = Path("./").resolve().absolute()

sys.path.append(str(src_path))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "My_travel_project.settings")

import django

django.setup()

from My_travel_project import settings
from travel_in_Russia.models import TelegramSubscriber


TG_BOT_TOKEN = settings.TG_BOT_TOKEN

Bot = telebot.TeleBot(TG_BOT_TOKEN)


@Bot.message_handler(commands=["start"])
def start_handler(message):
    chat_id = message.chat.id

    # Проверяем, зарегистрирован ли этот пользователь
    if not TelegramSubscriber.objects.filter(user_id=chat_id).exists():
        new_subscriber = TelegramSubscriber(user_id=chat_id)
        new_subscriber.save()
        Bot.reply_to(message, f"Привет! Ты теперь подписан.")
    else:
        Bot.reply_to(message, "Ты уже зарегистрирован!")


if __name__ == "__main__":
    Bot.polling(none_stop=True)
