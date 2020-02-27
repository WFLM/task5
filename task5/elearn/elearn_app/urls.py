from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CreateUserAPIView, LoginView, LogoutView


router = DefaultRouter()
router.register('login', LoginView, basename='login')


urlpatterns = [
    path("", include(router.urls)),
    path("register/", CreateUserAPIView.as_view(), name="register"),
    path("account/logout/", LogoutView.as_view(), name="logout")
]

