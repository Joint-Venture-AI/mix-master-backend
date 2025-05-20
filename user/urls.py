from django.urls import path

from .views import (
    ListCreateUserAPIView,
    RetrieveUpdateDestroyUserAPIView,
    ResendVerificationCodeView,
    LoginUserView,
    VerifyEmailView,
)

urlpatterns = [
    path("users", ListCreateUserAPIView.as_view()),
    path("user/verify", VerifyEmailView.as_view()),
    path("user/resend-verification-code", ResendVerificationCodeView.as_view()),
    path("user/me", RetrieveUpdateDestroyUserAPIView.as_view()),
    path("user/login", LoginUserView.as_view()),
]
