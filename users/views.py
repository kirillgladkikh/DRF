import json

import stripe
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend, OrderingFilter
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course
from users.filters import PaymentFilter
from users.models import Payments, Subscription, User
from users.serializers import PaymentSerializer, UserSerializer
from users.services import create_stripe_price, create_stripe_product, create_stripe_session


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payments.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]  # добавляем OrderingFilter
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]  # по умолчанию — новые первыми


# CRUD для модели User с использованием generics
class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UserListApiView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveApiView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserUpdateApiView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDestroyApiView(DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SubscriptionAPIView(APIView):
    """API для управления подпиской пользователя на курс."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response(
                {"error": "Поле 'course_id' обязательно для заполнения."}, status=status.HTTP_400_BAD_REQUEST
            )

        course_item = get_object_or_404(Course, id=course_id)
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        # Если подписка у пользователя на этот курс есть — удаляем её
        if subs_item.exists():
            subs_item.delete()
            message = "Подписка удалена"
            action = "unsubscribed"
        # Если подписки у пользователя на этот курс нет — создаём её
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "Подписка добавлена"
            action = "subscribed"

        return Response(
            {"message": message, "action": action, "course_id": course_item.id, "course_name": course_item.course_name}
        )


# для интеграции с Stripe
class PaymentCreateAPIView(CreateAPIView):
    queryset = Payments.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)

        # Валидация: выбран ли курс или урок (и только один)
        if payment.paid_course is None and payment.paid_lesson is None:
            raise ValidationError("Необходимо выбрать курс или урок для оплаты")
        if payment.paid_course and payment.paid_lesson:
            raise ValidationError("Нельзя одновременно выбрать и курс, и урок")

        # Берём сумму оплаты напрямую из поля amount модели Payments
        amount = payment.amount

        # Определяем источник данных (курс или урок) для названия и описания
        if payment.paid_course:
            source = payment.paid_course
            product_name = source.course_name
            product_description = source.course_description
        else:
            source = payment.paid_lesson
            product_name = source.lesson_name
            product_description = source.lesson_description

        try:
            # Создаём продукт в Stripe
            stripe_product = create_stripe_product(name=product_name, description=product_description)
            payment.stripe_product_id = stripe_product.get("id")

            # Создаём цену в Stripe — используем amount из платежа
            stripe_price = create_stripe_price(stripe_product=stripe_product, amount=amount)
            payment.stripe_price_id = stripe_price.get("id")

            # Формируем URL для перенаправления
            base_url = self.request.build_absolute_uri("/")
            success_url = f"{base_url}api/payment/callback/?status=success&payment_id={payment.id}"
            cancel_url = f"{base_url}api/payment/callback/?status=canceled&payment_id={payment.id}"

            # Создаём сессию оплаты в Stripe
            session_id, session_url = create_stripe_session(
                price_id=stripe_price.get("id"), success_url=success_url, cancel_url=cancel_url
            )

            # Сохраняем ID сессии и ссылку на оплату в БД
            payment.stripe_session_id = session_id
            payment.stripe_payment_link = session_url

            # Сохраняем платёж с обновлёнными полями
            payment.save()

            # Возвращаем ответ со ссылкой на оплату
            self.response_data = {
                "message": "Платёж создан. Перейдите по ссылке для оплаты.",
                "payment_id": payment.id,
                "payment_link": session_url,
                "status": payment.status,
            }

        except Exception as e:
            payment.status = "failed"
            payment.save()
            raise ValidationError(f"Ошибка при обработке платежа: {str(e)}")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if hasattr(self, "response_data"):
            response.data = self.response_data
        return response


@api_view(["GET"])
def payment_callback(request):
    status = request.GET.get("status")
    payment_id = request.GET.get("payment_id")

    # Проверка наличия payment_id
    if not payment_id:
        return JsonResponse({"error": "Отсутствует payment_id"}, status=400)

    try:
        # Поиск платежа по ID
        payment = Payments.objects.get(id=payment_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Платёж не найден"}, status=404)

    if status == "success":
        # Обновляем статус платежа в БД
        payment.status = "succeeded"
        payment.save()
        return JsonResponse(
            {"message": "Платёж успешно обработан!", "payment_id": payment.id, "status": payment.status}
        )
    elif status == "canceled":
        # Можно обновить статус на "canceled", если нужно
        payment.status = "canceled"
        payment.save()

        return JsonResponse({"message": "Оплата отменена. Попробуйте снова.", "payment_id": payment.id})
    else:
        return JsonResponse({"error": "Неизвестный статус"}, status=400)


@csrf_exempt  # Stripe не передаёт CSRF‑токен
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # Секретный ключ из настроек

    try:
        # Проверяем подпись вебхука — убеждаемся, что запрос от Stripe
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Неверный формат payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Неверная подпись — запрос не от Stripe
        return HttpResponse(status=400)

    # Обрабатываем событие
    handle_stripe_event(event)

    return HttpResponse(status=200)  # Подтверждаем получение


def handle_stripe_event(event):
    event_type = event["type"]
    data_object = event["data"]["object"]

    if event_type == "checkout.session.completed":
        # Платёж успешно завершён
        session = data_object
        payment_id = session.get("client_reference_id")  # ID платежа из метаданных

        try:
            payment = Payments.objects.get(id=payment_id)
            payment.status = "succeeded"
            payment.stripe_payment_intent_id = session.get("payment_intent")  # ID платёжного намерения
            payment.save()

            # Здесь можно добавить бизнес‑логику: открыть доступ к курсу/уроку, отправить email
        except Payments.DoesNotExist:
            pass  # Платёж не найден в БД

    elif event_type == "payment_intent.succeeded":
        # Аналогично обрабатываем успешное платёжное намерение
        pass

    elif event_type == "payment_intent.payment_failed":
        # Платёж не прошёл
        pass

    else:
        print(f"Необработанное событие: {event_type}")
