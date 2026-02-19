from django.contrib import admin
from django.urls import include, path
# from rest_framework.routers import DefaultRouter
# from lms.views import CourseViewSet


# # Создаём роутер и регистрируем ViewSet
# router = DefaultRouter()
# router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("lms/", include("lms.urls", namespace="lms")),
    # # Добавляем маршруты для Course через REST Framework
    # path('api/', include(router.urls)),
]
