from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail


class CustomUser(AbstractUser):
    
    email = models.EmailField(_('email address'), blank=False, unique=True)
    