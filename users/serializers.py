from rest_framework.serializers import ModelSerializer, StringRelatedField
from users.models import Payments, User


class PaymentSerializer(ModelSerializer):
    user = StringRelatedField()  # выводит username пользователя
    paid_course_name = StringRelatedField(source="paid_course.course_name")
    paid_lesson_name = StringRelatedField(source="paid_lesson.lesson_name")
    # paid_course = StringRelatedField()  # выводит название курса
    # paid_lesson = StringRelatedField()  # выводит название урока

    class Meta:
        model = Payments
        fields = [
            "id",
            "user",
            "payment_date",
            "paid_course",
            "paid_course_name",
            "paid_lesson",
            "paid_lesson_name",
            "amount",
            "payment_method",
        ]


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
