from django.urls import path

from .views import (
    ChangeUserPasswordView,
    ListCreateUserAPIView,
    RetrieveUpdateDestroyUserAPIView,
    ResendVerificationCodeView,
    RequestPasswordResetOTPView,
    VerifyOTPView,
    SetNewPasswordView,
    LoginUserView,
    VerifyEmailView,
)

urlpatterns = [
    path("users", ListCreateUserAPIView.as_view()),
    path("user/verify", VerifyEmailView.as_view()),
    path("user/resend-verification-code", ResendVerificationCodeView.as_view()),
    path("user/me", RetrieveUpdateDestroyUserAPIView.as_view()),
    path("user/login", LoginUserView.as_view()),
    path("user/change-password", ChangeUserPasswordView.as_view()),
    path("user/request-password-reset-otp", RequestPasswordResetOTPView.as_view()),
    path("user/verify-otp", VerifyOTPView.as_view()),
    path("user/set-new-password", SetNewPasswordView.as_view()),
]
