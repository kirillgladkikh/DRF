from celery import shared_task
from django.core.mail import send_mail

from config.settings import EMAIL_HOST_USER
from lms.models import Course


@shared_task
def send_course_update_notification(course_id, subscribers_email):
    course = Course.objects.get(id=course_id)
    for email in subscribers_email:
        send_mail(
            subject=f"Курс обновлён: {course.course_name}",
            message=f'Курс "{course.course_name}" был обновлён.',
            from_email=EMAIL_HOST_USER,
            recipient_list=[email],  # Отправляем каждому отдельно
            fail_silently=False,
        )
