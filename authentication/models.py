from django.contrib.auth.models import AbstractUser
from django.db import models
from authentication.managers import UserManager
from authentication.utils import validate_phone_number


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserModel(AbstractUser, TimeStampedModel):
    username = None
    phone_number = models.CharField(
        max_length=13,
        validators=[validate_phone_number],
        unique=True,
    )
    country = models.CharField(
        max_length=20,
        choices=[
            ('Uzbekistan', 'Uzbekistan'),
            ('Russia', 'Russia'),
            ('USA', 'USA')
        ],
    )
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['country']

    objects = UserManager()

    def clean(self):
        super().clean()
        if self.phone_number.startswith('+998'):
            self.country = 'Uzbekistan'
        elif self.phone_number.startswith('+7'):
            self.country = 'Russia'
        elif self.phone_number.startswith('+1'):
            self.country = 'USA'

    def __str__(self):
        return f"{self.phone_number} ({self.country})"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'user'
