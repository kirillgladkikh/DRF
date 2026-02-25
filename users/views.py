from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend, OrderingFilter
from .models import Payments
from .serializers import PaymentSerializer
from .filters import PaymentFilter

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payments.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]  # добавляем OrderingFilter
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']  # по умолчанию — новые первыми
