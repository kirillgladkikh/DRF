from rest_framework.serializers import ModelSerializer, SerializerMethodField
from lms.models import Course, Lesson


class CourseSerializer(ModelSerializer):
    lessons_count = SerializerMethodField()  # количество уроков в курсе
    lessons = SerializerMethodField()  # информация по всем урокам курса

    class Meta:
        model = Course
        fields = ["id", "course_name", "preview", "course_description", "lessons_count", "lessons"]


    def get_lessons_count(self, obj):
        """Метод для подсчёта количества уроков для текущего курса (obj)"""
        return obj.courses.count()  # используем related_name="courses" из модели Lesson

    def get_lessons(self, obj):
        """Метод для получения информации по всем урокам текущего курса"""
        lessons = obj.courses.all()
        serializer = LessonSerializer(lessons, many=True)
        return serializer.data


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
