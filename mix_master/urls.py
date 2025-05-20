
from django.contrib import admin
from django.urls import path, include
from jossauth import views as joss_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("user.urls")),
]
