from django.urls import path

from .views import (
    ListCreateUserAPIView,
    RetrieveUpdateDestroyUserAPIView,
    LoginUserView,
    VerifyEmailView,
)

urlpatterns = [
    path("users", ListCreateUserAPIView.as_view()),
    path("user/verify", VerifyEmailView.as_view()),
    path("user/me", RetrieveUpdateDestroyUserAPIView.as_view()),
    path("user/login", LoginUserView.as_view()),
]
