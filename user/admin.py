from django.contrib import admin

from .models import User
# Register your models here.



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    ordering = ["id"]
    list_display = [
        "id",
        "uid",
        "email",
        "name",
        "nickname",
        "phone",
        "dob",
        "gender",
        "country",
        "city",
        "address",
        "postal_code",
        "is_subscribed",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
        "updated_at",
    ]
