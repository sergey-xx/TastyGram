from django.contrib import admin

from .models import Tag, Ingredient, Recipe, RecipeIngredient

class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        # 'ingredient',
        # 'recipe',
        'amount',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
