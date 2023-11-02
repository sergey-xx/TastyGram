from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (Tag, Ingredient, Recipe, RecipeIngredient, Favorite,
                     ShoppingCart, Follow, User)

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
        'id',
        'author',
        'name',
        'text',
        'cooking_time',
        'get_tag',
        'get_in_shopping_card',
        'get_is_favorited',)

    def get_tag(self, obj):
        return ", ".join([p.name for p in obj.tags.all()])

    def get_in_shopping_card(self, obj):
        return ", ".join([p.username for p in obj.is_in_shopping_cart.all()])

    def get_is_favorited(self, obj):
        return ", ".join([p.username for p in obj.is_favorited.all()])


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',)


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'follower',
        'author'
    )

admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Follow, FollowAdmin)
# admin.site.register(User, UserAdmin)