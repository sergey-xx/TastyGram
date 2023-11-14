from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from recipes.models import Tag

User = get_user_model()


class Command(BaseCommand):
    """Команда для тестов и отладки."""

    help = 'Command to import ingredients'

    def handle(self, *args, **options):
        Tag.objects.get_or_create(name='fat',
                                  slug='fat',
                                  color='#DB7093')
        Tag.objects.get_or_create(name='sweet',
                                  slug='sweet',
                                  color='#DB7093')
