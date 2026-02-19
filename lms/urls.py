from rest_framework.routers import SimpleRouter
from lms.views import CourseViewSet
from lms.apps import LmsConfig

app_name = LmsConfig.name

router = SimpleRouter()
router.register("", CourseViewSet)

urlpatterns = []

urlpatterns += router.urls




# from django.urls import path
# from lms.apps import LmsConfig
# from lms.views import LessonListCreateView, LessonRetrieveUpdateDestroyView
#
#
# app_name = LmsConfig.name
#
# urlpatterns = [
#     # Эндпоинты для уроков
#     path('lessons/', LessonListCreateView.as_view(), name='lesson-list-create'),
#     path('lessons/<int:pk>/', LessonRetrieveUpdateDestroyView.as_view(), name='lesson-detail'),
#
# ]
