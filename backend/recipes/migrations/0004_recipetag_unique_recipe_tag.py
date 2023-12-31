# Generated by Django 3.2.16 on 2023-11-06 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_recipeingredient_unique_recipe_ingredient'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='recipetag',
            constraint=models.UniqueConstraint(fields=('tag', 'recipe'), name='unique_recipe_tag'),
        ),
    ]
