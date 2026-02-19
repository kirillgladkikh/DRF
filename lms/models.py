from django.db import models


class Course(models.Model):
    course_name = models.CharField(
        max_length=100,
        verbose_name="Наименование учебного курса",
        help_text="Введите наименование учебного курса"
    )
    preview = models.ImageField(
        upload_to="lms/previews/",
        verbose_name="Превью (картинка)",
        blank=True,
        null=True,
        help_text="Загрузите превью для учебного курса"
    )
    course_description = models.TextField(
        verbose_name="Описание учебного курса",
        help_text="Введите описание учебного курса"
    )

    class Meta:
        verbose_name = "Учебный курс"
        verbose_name_plural = "Учебные курсы"
        ordering = ["course_name"]

    def __str__(self):
        return self.course_name


class Lesson(models.Model):
    lesson_name = models.CharField(
        max_length=100, verbose_name="Наименование урока", help_text="Введите наименование урока"
    )
    lesson_description = models.TextField(verbose_name="Описание урока", help_text="Введите описание урока")
    preview = models.ImageField(
        upload_to="lms/previews/",
        verbose_name="Превью (картинка)",
        blank=True,
        null=True,
        help_text="Загрузите превью для урока"
    )
    video_url = models.URLField(verbose_name="Ссылка на видео урока", help_text="Введите ссылку на видео урока")
    lesson_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        verbose_name="Учебный курс",
        help_text="Введите наименование учебного курса к которому относится урок",
        null=True,
        blank=True,
        related_name="courses",
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["lesson_name", "lesson_course"]

    def __str__(self):
        return self.lesson_name




