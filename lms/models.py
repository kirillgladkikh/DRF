from django.db.models import CASCADE, SET_NULL, CharField, ForeignKey, ImageField, Model, TextField, URLField, DateTimeField

from config.settings import AUTH_USER_MODEL


class Course(Model):
    course_name = CharField(
        max_length=100, verbose_name="Наименование учебного курса", help_text="Введите наименование учебного курса"
    )
    preview = ImageField(
        upload_to="lms/previews/",
        verbose_name="Превью (картинка)",
        blank=True,
        null=True,
        help_text="Загрузите превью для учебного курса",
    )
    course_description = TextField(verbose_name="Описание учебного курса", help_text="Введите описание учебного курса")
    owner = ForeignKey(AUTH_USER_MODEL, on_delete=CASCADE, null=True, blank=True)
    updated_at = DateTimeField(
        auto_now=True,  # автоматически обновляется при каждом save()
        verbose_name="Дата последнего обновления",
        help_text="Дата и время последнего изменения курса"
    )

    class Meta:
        verbose_name = "Учебный курс"
        verbose_name_plural = "Учебные курсы"
        ordering = ["course_name"]

    def __str__(self):
        return self.course_name


class Lesson(Model):
    lesson_name = CharField(max_length=100, verbose_name="Наименование урока", help_text="Введите наименование урока")
    lesson_description = TextField(verbose_name="Описание урока", help_text="Введите описание урока")
    preview = ImageField(
        upload_to="lms/previews/",
        verbose_name="Превью (картинка)",
        blank=True,
        null=True,
        help_text="Загрузите превью для урока",
    )
    video_url = URLField(verbose_name="Ссылка на видео урока", help_text="Введите ссылку на видео урока")
    lesson_course = ForeignKey(
        Course,
        on_delete=SET_NULL,
        verbose_name="Учебный курс",
        help_text="Введите наименование учебного курса к которому относится урок",
        null=True,
        blank=True,
        related_name="courses",
    )
    owner = ForeignKey(AUTH_USER_MODEL, on_delete=CASCADE, null=True, blank=True)
    updated_at = DateTimeField(
        auto_now=True,  # автоматически обновляется при каждом save()
        verbose_name="Дата последнего обновления",
        help_text="Дата и время последнего изменения урока"
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["lesson_name", "lesson_course"]

    def __str__(self):
        return self.lesson_name
