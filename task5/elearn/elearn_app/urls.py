from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CreateUserAPIView, LoginView, LogoutView, UserViewSet, CourseViewSet

router = DefaultRouter()
router.register('login', LoginView, basename='login')
router.register('users', UserViewSet, basename='user-list')
router.register('course', CourseViewSet, basename="course-list")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", CreateUserAPIView.as_view(), name="register"),
    path("account/logout/", LogoutView.as_view(), name="logout")
]

