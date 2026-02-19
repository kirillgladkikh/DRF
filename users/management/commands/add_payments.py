from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import Payments, User  # Исправлен импорт User
from lms.models import Course, Lesson

class Command(BaseCommand):
    help = 'Добавляет 10 тестовых записей в таблицу payments'

    def handle(self, *args, **options):
        # Получаем несколько существующих курсов, уроков и пользователей
        courses = Course.objects.all()[:5]  # берём первые 5 курсов
        lessons = Lesson.objects.all()[:5]  # берём первые 5 уроков
        users = User.objects.all()[:3]     # берём первых 3 пользователей

        # Проверяем, что есть необходимые данные для создания платежей
        if len(courses) < 5 or len(lessons) < 5 or len(users) < 3:
            self.stdout.write(
                self.style.ERROR('Недостаточно данных в БД для создания тестовых платежей. '
                                'Требуется минимум 5 курсов, 5 уроков и 3 пользователя.')
            )
            return

        payments_data = [
            {
                'user': users[0],
                'payment_date': timezone.now(),
                'paid_course': courses[0],
                'paid_lesson': None,
                'amount': 1500.00,
                'payment_method': 'transfer'
            },
            {
                'user': users[1],
                'payment_date': timezone.now(),
                'paid_course': courses[1],
                'paid_lesson': None,
                'amount': 2000.00,
                'payment_method': 'cash'
            },
            {
                'user': users[2],
                'payment_date': timezone.now(),
                'paid_course': None,
                'paid_lesson': lessons[0],
                'amount': 500.00,
                'payment_method': 'transfer'
            },
            {
                'user': users[0],
                'payment_date': timezone.now(),
                'paid_course': courses[2],
                'paid_lesson': None,
                'amount': 1700.00,
                'payment_method': 'cash'
            },
            {
                'user': users[1],
                'payment_date': timezone.now(),
                'paid_course': None,
                'paid_lesson': lessons[1],
                'amount': 450.00,
                'payment_method': 'transfer'
            },
            {
                'user': users[2],
                'payment_date': timezone.now(),
                'paid_course': courses[3],
                'paid_lesson': None,
                'amount': 1900.00,
                'payment_method': 'cash'
            },
            {
                'user': users[0],
                'payment_date': timezone.now(),
                'paid_course': None,
                'paid_lesson': lessons[2],
                'amount': 600.00,
                'payment_method': 'transfer'
            },
            {
                'user': users[1],
                'payment_date': timezone.now(),
                'paid_course': courses[4],
                'paid_lesson': None,
                'amount': 1600.00,
                'payment_method': 'cash'
            },
            {
                'user': users[2],
                'payment_date': timezone.now(),
                'paid_course': None,
                'paid_lesson': lessons[3],
                'amount': 550.00,
                'payment_method': 'transfer'
            },
            {
                'user': users[0],
                'payment_date': timezone.now(),
                'paid_course': courses[0],  # повторяем курс для пользователя
                'paid_lesson': None,
                'amount': 1500.00,
                'payment_method': 'cash'
            }
        ]

        # Создаём платежи
        for payment_data in payments_data:
            payment = Payments.objects.create(**payment_data)
            self.stdout.write(
                self.style.SUCCESS(f'Создан платёж #{payment.id} для пользователя {payment_data["user"].email}')
            )
