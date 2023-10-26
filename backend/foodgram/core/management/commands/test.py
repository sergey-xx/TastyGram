from django.core.management.base import BaseCommand
from recipes.models import Recipe


class Command(BaseCommand):
    help = 'Command to import ingredients'

    def handle(self, *args, **options):
        recipe = Recipe.objects.all().first()
        
        print(recipe.ingredients)
