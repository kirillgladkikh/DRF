from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from users.views import PaymentViewSet

router = SimpleRouter()
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("lms/", include("lms.urls", namespace="lms")),
    path("", include(router.urls)),
    path('users/', include('users.urls', namespace='users')),
]
