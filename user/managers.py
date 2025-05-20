from django.contrib.auth.models import BaseUserManager
from django.db.models import Manager

from core.choices import StatusChoices


class StatusManager(Manager):
    def IS_ACTIVE(self):
        return self.filter(status=StatusChoices.ACTIVE)

    def IS_INACTIVE(self):
        return self.filter(status=StatusChoices.INACTIVE)

    def IS_REMOVED(self):
        return self.filter(status=StatusChoices.REMOVED)


class UserManager(BaseUserManager, StatusManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def IS_ACTIVE(self):
        # return super().IS_ACTIVE()
        return self.filter(is_active=True)

    def IS_INACTIVE(self):
        # return super().IS_INACTIVE()
        return self.filter(is_active=False)

    def IS_REMOVED(self):
        return super().IS_REMOVED()
