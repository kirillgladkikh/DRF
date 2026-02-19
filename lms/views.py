from rest_framework.viewsets import ModelViewSet
# from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from lms.models import Course, Lesson
from lms.serializers import CourseSerializer  #, LessonSerializer


# CRUD для модели Course с использованием ViewSet
class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer




# # Получение списка уроков и создание нового
# class LessonListCreateView(ListCreateAPIView):
#     queryset = Lesson.objects.all()
#     serializer_class = LessonSerializer
#
# # Получение, обновление и удаление конкретного урока
# class LessonRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
#     queryset = Lesson.objects.all()
#     serializer_class = LessonSerializer
