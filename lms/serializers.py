from rest_framework.serializers import ModelSerializer, SerializerMethodField
from lms.models import Course, Lesson


class CourseSerializer(ModelSerializer):
    lessons_count = SerializerMethodField()  # новое поле для количества уроков

    class Meta:
        model = Course
        fields = "__all__"

    def get_lessons_count(self, obj):
        """Метод для подсчёта количества уроков для текущего курса (obj)"""
        return obj.courses.count()  # используем related_name="courses" из модели Lesson


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
