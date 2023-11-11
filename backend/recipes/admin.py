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
    search_fields = ('name',)


class RecipeIngredientAdmin(admin.ModelAdmin):
    """Кастомизация админки модели Рецепты/Ингредиенты."""

    list_display = (
        'ingredient',
        'recipe',
        'amount',)


class TagInlineAdmin(admin.TabularInline):
    """Класс для вывода Тегов."""

    model = Recipe.tags.through


class IngredientInlineAdmin(admin.TabularInline):
    """Класс для вывода Ингредиентов."""

    model = Recipe.ingredients.through


class RecipeAdmin(admin.ModelAdmin):
    """Кастомизация админки модели Рецептов."""

    inlines = (IngredientInlineAdmin, TagInlineAdmin,)
    list_display = ('id',
                    'author',
                    'name',
                    'text',
                    'cooking_time',
                    'get_tag',
                    'get_in_shopping_card',
                    'get_is_favorited',
                    'pub_date',
                    'get_favorite_counter',
                    )

    search_fields = ('name', 'author__username', 'tags__name')
    list_filter = ('author', 'tags', )
    readonly_fields = ('get_favorite_counter',)

    def get_tag(self, obj):
        """Позволяет увидеть все добавленные Теги."""
        return ", ".join([p.name for p in obj.tags.all()])
    get_tag.short_description = 'Теги'

    def get_in_shopping_card(self, obj):
        """Позволяет увидеть все добавленные Список покупок."""
        return ", ".join([p.username for p in obj.is_in_shopping_cart.all()])
    get_in_shopping_card.short_description = 'В Списке покупок'

    def get_is_favorited(self, obj):
        """Позволяет увидеть все добавленные в Избранное."""
        return ", ".join([p.username for p in obj.is_favorited.all()])
    get_is_favorited.short_description = 'В избранном'

    def get_favorite_counter(self, obj):
        """Позволяет увидеть кол-во добавлений в Избранное."""
        return obj.is_favorited.all().count()
    get_favorite_counter.short_description = 'Всего в Избранном'


class FavoriteAdmin(admin.ModelAdmin):
    """Кастомизация админки модели Избранное."""

    list_display = ('user',
                    'recipe',)


class ShoppingCartAdmin(admin.ModelAdmin):
    """Кастомизация админки модели Списка покупок."""

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
