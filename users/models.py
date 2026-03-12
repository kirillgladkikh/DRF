from django.contrib.auth.models import AbstractUser
from django.db.models import (CASCADE, SET_NULL, CharField, DateTimeField, EmailField, ForeignKey, ImageField, Model,
                              PositiveIntegerField, URLField)

from lms.models import Course, Lesson


class User(AbstractUser):
    username = None
    email = EmailField(unique=True, verbose_name="Email")
    avatar = ImageField(
        upload_to="users/avatars/", verbose_name="Аватар", blank=True, null=True, help_text="Загрузите свой аватар"
    )
    phone = CharField(max_length=35, verbose_name="Телефон", blank=True, null=True, help_text="Введите номер телефона")
    country = CharField(max_length=50, verbose_name="Страна", blank=True, null=True, help_text="Введите страну")

    token = CharField(max_length=100, verbose_name="Token", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payments(Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счёт"),
        ("stripe", "Оплата через Stripe"),
    ]

    # пользователь, совершивший платеж
    user = ForeignKey(User, on_delete=CASCADE, verbose_name="Пользователь")
    # дата оплаты
    payment_date = DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    # оплаченный курс (может быть None, если оплачен только урок)
    paid_course = ForeignKey(Course, on_delete=SET_NULL, null=True, blank=True, verbose_name="Оплаченный курс")
    # отдельно оплаченный урок (может быть None, если оплачен курс)
    paid_lesson = ForeignKey(
        Lesson, on_delete=SET_NULL, null=True, blank=True, verbose_name="Отдельно оплаченный урок"
    )
    # сумма оплаты
    amount = PositiveIntegerField(verbose_name="Сумма оплаты", help_text="Укажите сумму оплаты")
    # способ оплаты
    payment_method = CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name="Способ оплаты")

    # поля для интеграции с Stripe
    stripe_session_id = CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID сессии в Stripe",
        help_text="Укажите ID сессии в Stripe",
    )
    stripe_payment_link = URLField(
        max_length=400,
        blank=True,
        null=True,
        verbose_name="Ссылка на оплату в Stripe",
        help_text="Укажите ссылку на оплату в Stripe",
    )
    # stripe_user = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True, verbose_name="Пользователь", help_text="Укажите пользователя")
    stripe_product_id = CharField(max_length=100, blank=True, null=True, verbose_name="ID продукта в Stripe")
    stripe_price_id = CharField(max_length=100, blank=True, null=True, verbose_name="ID цены в Stripe")
    status = CharField(
        max_length=20,
        choices=[
            ("pending", "Ожидает оплаты"),
            ("succeeded", "Успешно"),
            ("failed", "Ошибка"),
            ("canceled", "Отменён"),
        ],
        default="pending",
        verbose_name="Статус платежа",
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]  # сортировка по дате оплаты (новые первыми)

    def __str__(self):
        return f"Платеж от {self.user.email} на сумму {self.amount} ({self.payment_method})"


class Subscription(Model):
    """Модель подписки пользователя на обновления курса."""

    user = ForeignKey(User, on_delete=CASCADE, verbose_name="Пользователь", related_name="subscriptions")
    course = ForeignKey(Course, on_delete=CASCADE, verbose_name="Курс", related_name="subscribers")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        # Гарантируем уникальность: один пользователь может подписаться на курс только один раз
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user.email} → {self.course.course_name}"
