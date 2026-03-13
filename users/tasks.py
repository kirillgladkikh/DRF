from celery import shared_task
from django.utils import timezone
from users.models import User
from datetime import timedelta


@shared_task
def block_inactive_users():
    """
    Периодическая задача для блокировки пользователей,
    которые не заходили более месяца.
    """
    # Определяем дату, старше которой считаем пользователя неактивным
    one_month_ago = timezone.now() - timedelta(days=30)

    # Находим всех активных пользователей, которые не заходили больше месяца
    # Блокируем найденных пользователей
    count = User.objects.filter(
        is_active=True,
        last_login__lt=one_month_ago
    ).update(is_active=False)

    return f"Заблокировано пользователей: {count}"
