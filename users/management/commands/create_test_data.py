from django.core.management.base import BaseCommand

from lms.models import Course, Lesson
from users.models import User


class Command(BaseCommand):
    help = "Создаёт тестовые данные: 3 пользователя, 5 курсов и 5 уроков"

    def handle(self, *args, **options):
        # Создаём пользователей — используем email как уникальный идентификатор
        users_data = [
            {"email": "user1@example.com", "password": "testpass123"},
            {"email": "user2@example.com", "password": "testpass123"},
            {"email": "user3@example.com", "password": "testpass123"},
        ]

        created_users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data["email"],
                defaults={},  # В defaults не нужно указывать email — он уже в условии get_or_create
            )
            if created:
                user.set_password(user_data["password"])
                user.save()
                created_users.append(user)
                self.stdout.write(self.style.SUCCESS(f"Создан пользователь: {user.email}"))
            else:
                created_users.append(user)
                self.stdout.write(self.style.WARNING(f"Пользователь {user.email} уже существует"))

        # Создаём курсы (остаётся без изменений)
        courses_data = [
            "Основы Python",
            "Веб-разработка на Django",
            "Машинное обучение",
            "Базы данных SQL",
            "Алгоритмы и структуры данных",
        ]

        created_courses = []
        for course_name in courses_data:
            course, created = Course.objects.get_or_create(
                course_name=course_name, defaults={"course_description": f'Описание курса "{course_name}"'}
            )
            if created:
                created_courses.append(course)
                self.stdout.write(self.style.SUCCESS(f"Создан курс: {course.course_name}"))
            else:
                created_courses.append(course)
                self.stdout.write(self.style.WARNING(f'Курс "{course_name}" уже существует'))

        # Создаём уроки (по одному на каждый курс)
        lessons_data = [
            ("Введение в Python", "Первый урок по основам Python"),
            ("Основы Django", "Знакомство с фреймворком Django"),
            ("Введение в ML", "Основы машинного обучения"),
            ("SQL-запросы", "Работа с базами данных"),
            ("Структуры данных", "Основные структуры данных"),
        ]

        created_lessons = []
        for i, (lesson_name, lesson_desc) in enumerate(lessons_data):
            lesson, created = Lesson.objects.get_or_create(
                lesson_name=lesson_name,
                defaults={
                    "lesson_description": lesson_desc,
                    "video_url": f"https://example.com/video{i + 1}.mp4",
                    "lesson_course": created_courses[i],
                },
            )
            if created:
                created_lessons.append(lesson)
                self.stdout.write(self.style.SUCCESS(f"Создан урок: {lesson.lesson_name}"))
            else:
                created_lessons.append(lesson)
                self.stdout.write(self.style.WARNING(f'Урок "{lesson_name}" уже существует'))

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово! Создано: {len(created_users)} пользователей, "
                f"{len(created_courses)} курсов, {len(created_lessons)} уроков."
            )
        )
