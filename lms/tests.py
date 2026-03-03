from django.contrib.auth import get_user_model

from django.contrib.auth.models import Group
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from lms.models import Course, Lesson


User = get_user_model()  # Получаем кастомную модель пользователя

class LessonCRUDTests(APITestCase):

    def setUp(self):
        # Создаём клиента
        self.client = APIClient()

        # Создаём группы для тестирования прав доступа
        self.moder_group, _ = Group.objects.get_or_create(name='moders')

        # Создаём пользователей с разными правами — без указания username
        self.owner_user = User.objects.create(
            email='owner@example.com',
            password='testpass123'
        )
        # Устанавливаем корректный пароль (create не хэширует пароль автоматически)
        self.owner_user.set_password('testpass123')
        self.owner_user.save()

        self.moderator_user = User.objects.create(
            email='moderator@example.com',
            password='testpass123'
        )
        self.moderator_user.set_password('testpass123')
        self.moderator_user.save()

        self.other_user = User.objects.create(
            email='other@example.com',
            password='testpass123'
        )
        self.other_user.set_password('testpass123')
        self.other_user.save()

        # Добавляем модератора в группу moders
        self.moderator_user.groups.add(self.moder_group)

        # Создаём курс
        self.course = Course.objects.create(
            course_name='Тестовый курс',
            course_description='Описание тестового курса',
            owner=self.owner_user
        )

        # Создаём урок, принадлежащий owner_user
        self.lesson = Lesson.objects.create(
            lesson_name='Первый урок',
            lesson_description='Описание первого урока',
            video_url='https://www.youtube.com/watch?v=123',
            lesson_course=self.course,
            owner=self.owner_user
        )

        # URL endpoints
        self.list_url = '/lms/'
        self.detail_url = f'/lms/lessons/{self.lesson.pk}/'
        self.create_url = '/lms/lessons/create/'
        self.update_url = f'/lms/lessons/{self.lesson.pk}/update/'
        self.delete_url = f'/lms/lessons/{self.lesson.pk}/delete/'

    def test_create_lesson_as_owner(self):
        """Проверка создания урока владельцем"""
        self.client.force_authenticate(user=self.owner_user)
        data = {
            'lesson_name': 'Новый урок',
            'lesson_description': 'Описание нового урока',
            'video_url': 'https://www.youtube.com/watch?v=456',
            'lesson_course': self.course.pk,
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.last().lesson_name, 'Первый урок')

    def test_create_lesson_as_moderator(self):
        """Проверка, что модератор не может создавать уроки"""
        self.client.force_authenticate(user=self.moderator_user)
        data = {
            'lesson_name': 'Урок модератора',
            'lesson_description': 'Описание урока модератора',
            'video_url': 'https://www.youtube.com/watch?v=789',
            'lesson_course': self.course.pk,
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_lessons_as_owner(self):
        """Проверка получения списка уроков владельцем"""
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_lessons_as_moderator(self):
        """Проверка получения списка уроков модератором"""
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Модератор видит все уроки
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_retrieve_lesson_as_owner(self):
        """Проверка просмотра урока владельцем"""
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['lesson_name'], 'Первый урок')

    def test_retrieve_lesson_as_moderator(self):
        """Проверка просмотра урока модератором"""
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_lesson_as_other_user(self):
        """Проверка, что другой пользователь не видит урок"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_lesson_as_owner(self):
        """Проверка обновления урока владельцем"""
        self.client.force_authenticate(user=self.owner_user)
        data = {
            'lesson_name': 'Обновлённый урок',
            'lesson_description': 'Обновлённое описание',
            'video_url': 'https://www.youtube.com/watch?v=000',
        }
        response = self.client.put(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.lesson_name, 'Обновлённый урок')

    def test_update_lesson_as_moderator(self):
        """Проверка обновления урока модератором"""
        self.client.force_authenticate(user=self.moderator_user)
        data = {
            'lesson_name': 'Урок изменён модератором',
            'lesson_description': 'Описание изменено модератором',
            'video_url': 'https://www.youtube.com/watch?v=999',
        }
        response = self.client.put(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_lesson_as_other_user(self):
        """Проверка, что другой пользователь не может обновить урок"""
        self.client.force_authenticate(user=self.other_user)
        data = {
            'lesson_name': 'Попытка изменения',
            'lesson_description': 'Попытка описания',
            'video_url': 'https://www.youtube.com/watch?v=888',
        }
        response = self.client.put(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_as_owner(self):
        """Проверка удаления урока владельцем"""
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.lesson.pk).exists())

    def test_delete_lesson_as_moderator(self):
        """Проверка, что модератор не может удалить урок"""
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_as_other_user(self):
        """Проверка, что другой пользователь не может удалить урок"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Проверяем, что урок остался в базе данных
        self.assertTrue(Lesson.objects.filter(pk=self.lesson.pk).exists())
