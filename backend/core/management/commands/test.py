from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Count

from recipes.models import Follow

User = get_user_model()


class Command(BaseCommand):
    """Команда для тестов и отладки."""

    help = 'Command to import ingredients'

    def handle(self, *args, **options):
        objects = Follow.objects.annotate(count=Count('author__recipe'))
        for object in objects:
