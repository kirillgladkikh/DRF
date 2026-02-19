from rest_framework import viewsets, generics
from lms.models import Course, Lesson
from lms.serializers import CourseSerializer, LessonSerializer


# CRUD для модели Course с использованием ViewSet
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


# Получение списка уроков и создание нового
class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

# Получение, обновление и удаление конкретного урока
class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
