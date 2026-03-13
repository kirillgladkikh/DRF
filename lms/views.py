from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from lms.models import Course, Lesson
from lms.paginators import CustomPagination
from lms.serializers import CourseSerializer, LessonSerializer
from lms.tasks import send_course_update_notification  # задача Celery
from users.permissions import IsModer, IsOwner


# CRUD для модели Course с использованием ViewSet
class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        # Проверка на генерацию схемы Swagger
        if getattr(self, "swagger_fake_view", False):
            return self.queryset.none()  # Возвращаем пустой QuerySet для схемы

        qs = super().get_queryset()

        # Проверяем, что пользователь аутентифицирован
        if not self.request.user.is_authenticated:
            return qs.none()  # Для неавторизованных — пустой набор

        # Проверяем наличие группы "moders"
        if not self.request.user.groups.filter(name="moders").exists():
            # Обычные пользователи видят только свои курсы
            qs = qs.filter(owner=self.request.user)

        return qs

    def get_permissions(self):
        # Решение для Задания 3
        if self.action in ["create"]:
            self.permission_classes = (~IsModer,)
        elif self.action in ["list", "update", "retrieve", "destroy"]:
            self.permission_classes = (~IsModer | IsOwner,)
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["patch"])
    def notify_update(self, request, pk=None):
        """
        Обновление курса с отправкой уведомлений.
        URL автоматически станет: /courses/{id}/notify_update/
        Метод: PATCH
        """
        course = self.get_object()  # Получаем объект курса по ID из URL
        serializer = self.get_serializer(course, data=request.data, partial=True)

        if serializer.is_valid():
            # Сохраняем обновлённый курс
            updated_course = serializer.save()

            # Получаем всех подписчиков курса
            from lms.models import Subscription  # Импорт модели подписчиков

            subscribers = Subscription.objects.filter(course=updated_course).select_related("user")

            # Извлекаем список email-адресов подписчиков
            subscribers_email = [subscriber.user.email for subscriber in subscribers if subscriber.user.email]

            if subscribers_email:  # Если есть email-адреса для отправки
                # Запускаем асинхронную задачу по отправке уведомлений
                from lms.tasks import send_course_update_notification

                send_course_update_notification.delay(updated_course.id, subscribers_email)

                return Response(
                    {
                        "message": "Курс успешно обновлён, уведомления отправлены подписчикам",
                        "course": serializer.data,
                        "email_count": len(subscribers_email),  # Добавляем количество отправленных писем
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                # Если нет валидных email-адресов
                return Response(
                    {
                        "message": "Курс успешно обновлён, но email-адреса для отправки уведомлений отсутствуют",
                        "course": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# CRUD для модели Lesson с использованием generics
class LessonCreateApiView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (
        IsAuthenticated,
        ~IsModer,
    )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListApiView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = CustomPagination
    permission_classes = (
        IsAuthenticated,
        IsModer | IsOwner,
    )

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.groups.filter(name="moders").exists():
            qs = qs.filter(owner=self.request.user)
        return qs


class LessonRetrieveApiView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (
        IsAuthenticated,
        IsModer | IsOwner,
    )


class LessonUpdateApiView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (
        IsAuthenticated,
        IsModer | IsOwner,
    )


class LessonDestroyApiView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (
        IsAuthenticated,
        IsOwner,
    )
