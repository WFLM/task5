from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import CreateUserAPIView, \
    LoginView, LogoutView, UserViewSet, \
    CourseViewSet, LectureViewSet, HomeworkViewSet, HomeworkInstanceViewSet, HomeworkInstanceCommentViewSet, \
    HomeworkInstanceMarkViewSet

router = DefaultRouter()
router.register('login', LoginView, basename='login')
router.register('users', UserViewSet, basename='user')
router.register('course', CourseViewSet, basename='course')
router.register('lecture', LectureViewSet, basename='lecture')
router.register('homework', HomeworkViewSet, basename='homework')
router.register('homework_instance', HomeworkInstanceViewSet, basename="homework-instance")
router.register("homework_instance_comment", HomeworkInstanceCommentViewSet, basename="homework-instance-comment")
router.register("homework_instance_mark", HomeworkInstanceMarkViewSet, basename="homework-instance-mark")

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", include(router.urls)),
    path("register/", CreateUserAPIView.as_view(), name="register"),
    path("account/logout/", LogoutView.as_view(), name="logout"),

    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

