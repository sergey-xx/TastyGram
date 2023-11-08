# Generated by Django 3.2.16 on 2023-11-08 12:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_recipetag_unique_recipe_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата публикации'),
            preserve_default=False,
        ),
    ]