from rest_framework.serializers import ModelSerializer, StringRelatedField
from users.models import Payments

class PaymentSerializer(ModelSerializer):
    user = StringRelatedField()  # выводит username пользователя
    paid_course = StringRelatedField()  # выводит название курса
    paid_lesson = StringRelatedField()  # выводит название урока

    class Meta:
        model = Payments
        fields = ['id', 'user', 'payment_date', 'paid_course', 'paid_lesson', 'amount', 'payment_method']
