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
    slug = AutoSlugField(populate_from = generate_user_slug, unique=True)
    # username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    # first_name = models.CharField(max_length=255)
    # last_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, blank=True)
    phone = PhoneNumberField(blank=True)
    profile_image = models.ImageField(upload_to="media/user/profile_images/")
    cover_image = models.ImageField(upload_to="media/user/cover_images/")
    bio = models.TextField()
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=GenderChoices, blank=True)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    address = models.TextField()
    postal_code = models.IntegerField()
    is_subscribed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    
    objects = UserManager()
    
    USERNAME_FIELD = "email"
    
    def __str__(self):
        return self.email
    


