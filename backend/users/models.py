from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Кастомная модель Пользователей."""

    email = models.EmailField('email адрес', blank=False, unique=True)
