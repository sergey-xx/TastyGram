from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель Пользователей."""

    email = models.EmailField('email адрес', blank=False, unique=True)
