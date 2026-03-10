from rest_framework import serializers

from lms.models import Course, Lesson
from lms.validators import validate_youtube

# from rest_framework.serializers import ModelSerializer, SerializerMethodField



class LessonShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "lesson_name", "preview", "video_url"]


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()  # количество уроков в курсе
    lessons = LessonShortSerializer(many=True)  # используем новый сериализатор  # информация по всем урокам курса

    class Meta:
        model = Course
        fields = ["id", "course_name", "preview", "course_description", "lessons_count", "lessons"]

    def get_lessons_count(self, obj):
        """Метод для подсчёта количества уроков для текущего курса (obj)"""
        return obj.lesson_set.count()  # стало
        # return obj.courses.count()  # используем related_name="courses" из модели Lesson


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(validators=[validate_youtube], help_text="Только ссылки youtube.com")

    class Meta:
        model = Lesson
        fields = "__all__"
