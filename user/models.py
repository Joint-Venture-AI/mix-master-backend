from datetime import timedelta
from django.utils import timezone
import random

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from autoslug import AutoSlugField
from phonenumber_field.modelfields import PhoneNumberField

from .utils import generate_user_slug
from .choices import GenderChoices
from .managers import UserManager

from core.models import BaseModel


# Create your models here.


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    slug = AutoSlugField(populate_from=generate_user_slug, unique=True)
    # username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    # first_name = models.CharField(max_length=255)
    # last_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, blank=True, null=True)
    phone = PhoneNumberField(blank=True)
    profile_image = models.ImageField(
        upload_to="media/user/profile_images/", blank=True
    )
    cover_image = models.ImageField(upload_to="media/user/cover_images/", blank=True)
    bio = models.TextField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10, choices=GenderChoices, blank=True, null=True
    )
    country = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    postal_code = models.CharField(blank=True, null=True)
    is_subscribed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    @classmethod
    def joss_auth(cls, email:str, password: str) -> tuple[bool, str]:
        user = cls.objects.filter(email=email).first()
        if user is not None:
            if user.check_password(password):
                return True, 'Success'
            return False, 'Invalid password'
        return False, 'User not found'
    
    def __str__(self):
        return self.email
    
    


# user/models.py (continued)


class EmailVerification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(random.randint(1000, 9999))
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)
    
    
class PasswordResetOtp(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=4)
    is_verified = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.otp:
            self.otp = str(random.randint(0000, 9999))
        
        super().save(*args, **kwargs)
    
    @property        
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)
    
    def __str__(self):
        return f"Email: {self.user.email} - OTP: {self.otp}"
