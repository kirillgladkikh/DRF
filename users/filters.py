import django_filters

from users.models import Payments


class PaymentFilter(django_filters.FilterSet):
    paid_course = django_filters.NumberFilter(field_name="paid_course__id", lookup_expr="exact")
    paid_lesson = django_filters.NumberFilter(field_name="paid_lesson__id", lookup_expr="exact")
    payment_method = django_filters.CharFilter(field_name="payment_method", lookup_expr="exact")
    ordering = django_filters.OrderingFilter(
        fields=(("payment_date", "payment_date"),),
        field_labels={
            "payment_date": "Дата оплаты",
        },
    )

    class Meta:
        model = Payments
        fields = ["paid_course", "paid_lesson", "payment_method"]
