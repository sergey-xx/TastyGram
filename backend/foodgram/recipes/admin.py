from django.contrib import admin

from .models import Tag, Ingredient, Recipe, RecipeIngredient, Favorite

class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient',
        'recipe',
        'amount',)


class RecipeAdmin(admin.ModelAdmin):
    list_display= (
        'author',
        'name',
        'text',
        'cooking_time',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
