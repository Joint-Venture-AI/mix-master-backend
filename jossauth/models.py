import datetime
from django.utils import timezone as tz
from django.db import models
from user.models import User
from utils import keygen, operations as ops


class JossToken(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='joss_tokens')
    access_token = models.CharField(max_length=150, unique=True, default='')
    refresh_token = models.CharField(max_length=150, unique=True, default='')
    access_token_lifetime = models.IntegerField(default=7) #days
    refresh_token_lifetime = models.IntegerField(default=20) #days
    created_at = models.DateTimeField(auto_now_add=True)
    refreshed_at = models.DateTimeField(default=tz.make_aware(datetime.datetime.now()))
    refresh_count = models.IntegerField(default=0)
    
    @classmethod
    def get_user(cls, request) -> User | None:
        access_token = ops.extract_auth_token(request)
        if access_token is not None:
            joss = cls.objects.filter(access_token=access_token).first()
            if joss is not None: return joss.user
        return None
    
    def __generate_token(self, token_type: str, wing_len: int) -> str:
        kg = keygen.KeyGen()
        gen_token = lambda: kg.alphanumeric_key(wing_len) + kg.datetime_key() + kg.alphanumeric_key(wing_len)
        token = gen_token()
        while self.__class__.objects.filter(**{f'{token_type}_token':token}).exists():
            token = gen_token()
        return token
    
    def __generate_access_token(self) -> str:
        return self.__generate_token('access', 30)
    
    def __generate_refresh_token(self) -> str:
        return self.__generate_token('refresh', 40)
    
    def refresh(self) -> bool:
        if self.refresh_token_has_lifetime:
            self.access_token = self.__generate_access_token()
            self.refreshed_at = tz.make_aware(datetime.datetime.now())
            self.refresh_count += 0; self.save()
            return True
        return False
    
    @property
    def remaining_days(self) -> tuple[int, int]:
        return (tz.make_aware(datetime.datetime.now()) - self.refreshed_at).days
    
    @property
    def access_token_life_time_left_in_days(self):
        return self.access_token_lifetime - self.remaining_days
    
    @property
    def refresh_token_life_time_left_in_days(self):
        return self.refresh_token_lifetime - self.remaining_days
    
    @property
    def access_token_has_lifetime(self) -> bool:
        return self.access_token_life_time_left_in_days >= 0
    
    @property
    def refresh_token_has_lifetime(self) -> bool:
        return self.refresh_token_life_time_left_in_days >= 0
    
    @property
    def token_details(self) -> dict:
        return dict(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            access_token_lifetime=self.access_token_lifetime,
            refresh_token_lifetime=self.refresh_token_lifetime,
            access_token_lifetime_left=self.access_token_life_time_left_in_days,
            refresh_token_lifetime_left=self.refresh_token_life_time_left_in_days
        )
    
    def save(self, *args, **kwargs) -> None:
        if not self.access_token: self.access_token = self.__generate_access_token()
        if not self.refresh_token: self.refresh_token = self.__generate_refresh_token()

        super().save(*args, **kwargs)
    
    
