from django.contrib.auth.models import AbstractUser
from django.db.models import Model, EmailField, ImageField, CharField, ForeignKey, CASCADE, DateTimeField, SET_NULL, PositiveIntegerField
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
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счёт'),
    ]

    # пользователь, совершивший платеж
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        verbose_name="Пользователь"
    )
    # дата оплаты
    payment_date = DateTimeField(
        auto_now_add=True,
        verbose_name="Дата оплаты"
    )
    # оплаченный курс (может быть None, если оплачен только урок)
    paid_course = ForeignKey(
        Course,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        verbose_name="Оплаченный курс"
    )
    # отдельно оплаченный урок (может быть None, если оплачен курс)
    paid_lesson = ForeignKey(
        Lesson,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        verbose_name="Отдельно оплаченный урок"
    )
    # сумма оплаты
    amount = PositiveIntegerField(  # заменяем DecimalField на PositiveIntegerField
        # max_digits=10,
        # decimal_places=2,
        verbose_name="Сумма оплаты"
    )
    # способ оплаты
    payment_method = CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Способ оплаты"
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ['-payment_date']  # сортировка по дате оплаты (новые первыми)

    def __str__(self):
        return f"Платеж от {self.user.email} на сумму {self.amount} ({self.payment_method})"  # используем email вместо username
