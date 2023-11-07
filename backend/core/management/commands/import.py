from io import open
import json
import os
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def ingredient_import_json():
    """Импорт объектов ингредиентов из json-файла."""
    os.chdir('..')
    os.chdir('data')
    full_path = os.getcwd()
    with open(full_path + r'/ingredients.json',
              encoding='utf-8') as f:
        data = json.load(f)
        for object in data:
            try:
                Ingredient.objects.get_or_create(
                        name=object["name"],
                        measurement_unit=object["measurement_unit"])
                print(f'Объект импортирован: {object["name"]},'
                      f'{object["measurement_unit"]}')
            except ImportError:
                print('Ошибка импортирования')


class Command(BaseCommand):
    """Импорт ингредиентов."""

    help = 'Command to import ingredients'

    def handle(self, *args, **options):
        ingredient_import_json()
