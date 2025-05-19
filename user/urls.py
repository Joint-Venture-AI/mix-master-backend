from django.urls import path

from .views import ListCreateUserAPIView, RetrieveUpdateDestroyUserAPIView, LoginUserSerializer

urlpatterns = [
    path("users", ListCreateUserAPIView.as_view()),
    path("user/me", RetrieveUpdateDestroyUserAPIView.as_view()),
    path("user/login", LoginUserSerializer.as_view()),
]