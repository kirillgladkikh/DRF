from rest_framework.serializers import ModelSerializer, StringRelatedField

from users.models import Payments, Subscription, User


class PaymentSerializer(ModelSerializer):
    user = StringRelatedField()
    paid_course_name = StringRelatedField(source="paid_course.course_name")
    paid_lesson_name = StringRelatedField(source="paid_lesson.lesson_name")

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
            # поля для интеграции с Stripe
            "stripe_product_id",
            "stripe_price_id",
            "stripe_session_id",
            "stripe_payment_link",
            "status",
        ]
        # поля для интеграции с Stripe
        read_only_fields = [
            "stripe_product_id",
            "stripe_price_id",
            "stripe_session_id",
            "stripe_payment_link",
            "status",
        ]


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class SubscriptionSerializer(ModelSerializer):
    user_email = StringRelatedField(source="user.email", read_only=True)
    course_name = StringRelatedField(source="course.course_name", read_only=True)

    class Meta:
        model = Subscription
        fields = ["id", "user", "user_email", "course", "coursename", "created_at"]
