from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Command to import ingredients'

    def handle(self, *args, **options):
        pass
