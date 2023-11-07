from django.contrib.auth import get_user_model
from django.contrib import admin

from .models import (Tag, Ingredient, Recipe, RecipeIngredient, Favorite,
                     ShoppingCart, Follow, RecipeTag)

User = get_user_model()


class TagAdmin(admin.ModelAdmin):
    """Кастомизация админки модели Тэгов."""

    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    """Кастомизация админки модели Ингредиентов."""

    list_display = ('pk', 'name', 'measurement_unit')


class RecipeIngredientAdmin(admin.ModelAdmin):
    """Кастомизация админки модели Рецепты/Ингредиенты."""

    list_display = (
        'ingredient',
        'recipe',
        'amount',)


class RecipeAdmin(admin.ModelAdmin):
    """Кастомизация админки модели Рецептов."""

    list_display = (
        'id',
        'author',
        'name',
        'text',
        'cooking_time',
        'get_tag',
        'get_in_shopping_card',
        'get_is_favorited',)

    def get_tag(self, obj):
        """Позволяет увидеть все добавленные Тэги."""
        return ", ".join([p.name for p in obj.tags.all()])

    def get_in_shopping_card(self, obj):
        """Позволяет увидеть все добавленные Корзины."""
        return ", ".join([p.username for p in obj.is_in_shopping_cart.all()])

    def get_is_favorited(self, obj):
        """Позволяет увидеть все добавленные в Избранное."""
        return ", ".join([p.username for p in obj.is_favorited.all()])


class FavoriteAdmin(admin.ModelAdmin):
    """Кастомизация админки модели Любимых."""

    list_display = (
        'user',
        'recipe',)


class ShoppingCartAdmin(admin.ModelAdmin):
    """Кастомизация админки модели Корзины."""

    list_display = (
        'user',
        'recipe',)


class FollowAdmin(admin.ModelAdmin):
    """Кастомизация админки модели Подписки."""

    list_display = (
        'follower',
        'author'
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(RecipeTag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Follow, FollowAdmin)
