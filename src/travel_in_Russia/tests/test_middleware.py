from datetime import datetime
import os
import sys
from pathlib import Path
from django.http import HttpResponse
import pytest
from django.test import RequestFactory

src_path = Path("./src").resolve().absolute()

sys.path.append(str(src_path))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "My_travel_project.settings")

import django

django.setup()

from django.contrib.auth.models import User
from travel_in_Russia.middleware.admin_middleware import AdminMiddleware, Bot
from travel_in_Russia.models import TelegramSubscriber

from unittest.mock import Mock, patch


@pytest.fixture
def rf():
    """Request factory instance."""
    return RequestFactory()


@pytest.fixture
def admin_user():
    """Создание суперпользователя"""
    return User.objects.create_superuser(
        username="admin", email="admin@example.com", password="adminpass"
    )


@pytest.fixture
def subscriber():
    """Создание подписчика"""
    return TelegramSubscriber.objects.create(user_id=123456789)


@pytest.mark.django_db
def test_admin_middleware_notification(admin_user, subscriber, rf):
    """Проверяем, что при доступе к /admin отправляются уведомления"""
    # Подготовим запрос
    request = rf.get("/admin/")
    request.user = admin_user

    # Имитируем получение ответа
    response = HttpResponse(status=200)

    # Патчим метод отправки сообщений в Telegram
    with patch.object(Bot, "send_message") as mock_bot:
        # Запустим middleware
        middleware = AdminMiddleware(lambda req: response)
        result = middleware(request)

        # Убедимся, что уведомление было отправлено
        mock_bot.assert_called_once_with(
            subscriber.user_id,
            f"✨ Новый вход в админпанель!\n"
            f"⏰ Время: {datetime.now()}\n"
            f"👤 Пользователь: {admin_user.username}",
        )

    # Проверим возвращаемый результат
    assert result.status_code == 200
