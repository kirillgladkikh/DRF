from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from lms.models import Course, Lesson
from lms.paginators import CustomPagination
from lms.serializers import CourseSerializer, LessonSerializer
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

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     if not self.request.user.groups.filter(name="moders").exists():
    #         qs = qs.filter(owner=self.request.user)
    #     return qs

    def get_permissions(self):
        # Решение для Задания 3
        if self.action in ["create"]:
            self.permission_classes = (~IsModer,)
        elif self.action in ["list", "update", "retrieve", "destroy"]:
            self.permission_classes = (~IsModer | IsOwner,)
        return super().get_permissions()

        # # Решение для Задания 2
        # if self.action in ["create", "destroy"]:
        #     self.permission_classes = (~IsModer,)
        # elif self.action in ["update", "retrieve"]:
        #     self.permission_classes = (IsModer,)
        # return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


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
