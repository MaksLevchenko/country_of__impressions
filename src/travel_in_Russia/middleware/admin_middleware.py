import datetime
import telebot

from My_travel_project import settings
from travel_in_Russia.models import TelegramSubscriber


TG_BOT_TOKEN = settings.TG_BOT_TOKEN
Bot = telebot.TeleBot(TG_BOT_TOKEN)


class AdminMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (
            request.path.startswith("/admin")
            and request.user.is_authenticated
            and request.user.is_staff
        ):
            subscribers = TelegramSubscriber.objects.all()
            for sub in subscribers:
                notification_text = (
                    f"✨ Новый вход в админпанель!\n"
                    f"⏰ Время: {datetime.datetime.now()}\n"
                    f"👤 Пользователь: {request.user.username}"
                )
                Bot.send_message(sub.user_id, notification_text)
        return response
