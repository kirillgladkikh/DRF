from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from lms.models import Course
from users.models import Subscription

User = get_user_model()

class SubscriptionTests(APITestCase):
    def setUp(self):
        # Создаём клиента
        self.client = APIClient()

        # Создаём группы для тестирования прав доступа
        self.moder_group, _ = Group.objects.get_or_create(name='moders')

        # Создаём пользователей с разными правами
        self.user1 = User.objects.create(
            email='user1@example.com',
            password='testpass123'
        )
        self.user1.set_password('testpass123')
        self.user1.save()

        self.user2 = User.objects.create(
            email='user2@example.com',
            password='testpass123'
        )
        self.user2.set_password('testpass123')
        self.user2.save()

        self.moderator = User.objects.create(
            email='moderator@example.com',
            password='testpass123'
        )
        self.moderator.set_password('testpass123')
        self.moderator.save()
        self.moderator.groups.add(self.moder_group)

        # Создаём курсы
        self.course1 = Course.objects.create(
            course_name='Курс 1',
            course_description='Описание курса 1',
            owner=self.user1
        )

        self.course2 = Course.objects.create(
            course_name='Курс 2',
            course_description='Описание курса 2',
            owner=self.user2
        )

        # URL endpoint для подписки
        self.subscription_url = '/users/subscription/'

    def test_subscribe_to_course_as_authenticated_user(self):
        """Проверка подписки на курс авторизованным пользователем."""
        self.client.force_authenticate(user=self.user1)
        data = {
            'course_id': self.course1.pk
        }
        response = self.client.post(self.subscription_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertEqual(response.data['action'], 'subscribed')
        self.assertEqual(response.data['course_id'], self.course1.pk)
        self.assertEqual(response.data['course_name'], self.course1.course_name)

        # Проверяем, что подписка действительно создана
        subscription = Subscription.objects.filter(user=self.user1, course=self.course1)
        self.assertTrue(subscription.exists())

    def test_unsubscribe_from_course(self):
        """Проверка отмены подписки на курс."""
        # Сначала создаём подписку
        Subscription.objects.create(user=self.user1, course=self.course1)

        self.client.force_authenticate(user=self.user1)
        data = {
            'course_id': self.course1.pk
        }
        response = self.client.post(self.subscription_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertEqual(response.data['action'], 'unsubscribed')

        # Проверяем, что подписка удалена
        subscription = Subscription.objects.filter(user=self.user1, course=self.course1)
        self.assertFalse(subscription.exists())

    def test_subscribe_to_nonexistent_course(self):
        """Проверка попытки подписки на несуществующий курс."""
        self.client.force_authenticate(user=self.user1)
        data = {
            'course_id': 9999  # несуществующий ID
        }
        response = self.client.post(self.subscription_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscribe_without_course_id(self):
        """Проверка отправки запроса без указания course_id."""
        self.client.force_authenticate(user=self.user1)
        data = {}  # нет course_id
        response = self.client.post(self.subscription_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Поле \'course_id\' обязательно для заполнения.')

    def test_multiple_subscriptions_for_same_user_and_course(self):
        """Проверка, что нельзя создать несколько подписок на один курс для одного пользователя."""
        self.client.force_authenticate(user=self.user1)

        # Первая подписка
        data1 = {'course_id': self.course1.pk}
        response1 = self.client.post(self.subscription_url, data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Вторая попытка подписки на тот же курс
        data2 = {'course_id': self.course1.pk}
        response2 = self.client.post(self.subscription_url, data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)  # должно переключиться на отмену
        self.assertEqual(response2.data['message'], 'Подписка удалена')

    def test_subscribe_as_moderator(self):
        """Проверка возможности модератора подписываться на курсы."""
        self.client.force_authenticate(user=self.moderator)
        data = {
            'course_id': self.course2.pk
        }
        response = self.client.post(self.subscription_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')

        subscription = Subscription.objects.filter(user=self.moderator, course=self.course2)
        self.assertTrue(subscription.exists())

    def test_subscribe_as_unauthenticated_user(self):
        """Проверка попытки подписаться без аутентификации."""
        data = {
            'course_id': self.course1.pk
        }
        response = self.client.post(self.subscription_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscribe_to_course_owned_by_user(self):
        """Проверка подписки пользователя на собственный курс."""
        self.client.force_authenticate(user=self.user1)
        data = {
            'course_id': self.course1.pk  # user1 — владелец курса
        }
        response = self.client.post(self.subscription_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')

        subscription = Subscription.objects.filter(user=self.user1, course=self.course1)
        self.assertTrue(subscription.exists())

    def test_list_subscriptions(self):
        """Проверка получения списка подписок пользователя (если есть соответствующий endpoint)."""
        # Если в проекте есть endpoint для получения списка подписок, можно добавить тест:
        # Например: /users/subscriptions/
        # Для этого нужно добавить соответствующий view и URL
        pass  # Заглушка — реализация зависит от наличия endpoint

    def test_concurrent_subscription_operations(self):
        """Проверка корректности операций подписки/отписки при последовательных запросах."""
        self.client.force_authenticate(user=self.user2)

        # Подписываемся
        data_sub = {'course_id': self.course1.pk}
        response_sub = self.client.post(self.subscription_url, data_sub, format='json')

        # Проверяем успешность подписки
        self.assertEqual(response_sub.status_code, status.HTTP_200_OK)
        self.assertEqual(response_sub.data['message'], 'Подписка добавлена')
        self.assertEqual(response_sub.data['action'], 'subscribed')

        # Проверяем, что подписка создана в БД
        subscription = Subscription.objects.filter(user=self.user2, course=self.course1)
        self.assertTrue(subscription.exists())

        # Теперь отписываемся
        data_unsub = {'course_id': self.course1.pk}
        response_unsub = self.client.post(self.subscription_url, data_unsub, format='json')

        # Проверяем успешность отписки
        self.assertEqual(response_unsub.status_code, status.HTTP_200_OK)
        self.assertEqual(response_unsub.data['message'], 'Подписка удалена')
        self.assertEqual(response_unsub.data['action'], 'unsubscribed')

        # Проверяем, что подписка удалена из БД
        subscription_after_unsub = Subscription.objects.filter(user=self.user2, course=self.course1)
        self.assertFalse(subscription_after_unsub.exists())

        # И снова подписываемся для проверки цикличности
        data_resub = {'course_id': self.course1.pk}
        response_resub = self.client.post(self.subscription_url, data_resub, format='json')

        # Проверяем повторную подписку
        self.assertEqual(response_resub.status_code, status.HTTP_200_OK)
        self.assertEqual(response_resub.data['message'], 'Подписка добавлена')
        self.assertEqual(response_resub.data['action'], 'subscribed')

        # Проверяем, что подписка снова создана
        subscription_final = Subscription.objects.filter(user=self.user2, course=self.course1)
        self.assertTrue(subscription_final.exists())
