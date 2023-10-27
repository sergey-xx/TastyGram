from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

from recipes.models import Favorite, Recipe


from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Command to import ingredients'

    def handle(self, *args, **options):
        
        user = get_object_or_404(User, id=2)
        recipe = get_object_or_404(Recipe, id=1)
        result = Favorite.objects.get(user=user, recipe=recipe)
        print(result)
