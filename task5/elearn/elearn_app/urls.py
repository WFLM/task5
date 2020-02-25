from django.urls import path
from .views import CreateUserAPIView, AuthenticateUserAPIView

urlpatterns = [
    path("create/", CreateUserAPIView.as_view(), name="elearn_app"),
    path("obtain_token/", AuthenticateUserAPIView.as_view())
]
