from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from lms.models import Course, Lesson
from lms.serializers import CourseSerializer, LessonSerializer

from users.permissions import IsModer, IsOwner


# CRUD для модели Course с использованием ViewSet
class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

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

        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# CRUD для модели Lesson с использованием generics
class LessonCreateApiView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, ~IsModer,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        # new_lesson = serializer.save()
        # new_lesson.owner = self.request.user
        # new_lesson.save()


class LessonListApiView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, IsModer | IsOwner,)


class LessonRetrieveApiView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, IsModer | IsOwner,)


class LessonUpdateApiView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, IsModer | IsOwner,)


class LessonDestroyApiView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    # permission_classes = (IsAuthenticated, ~IsModer | IsOwner,)
