from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (Favorite, Follow, Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, ShoppingCart, Tag)

User = get_user_model()


class TagAdmin(admin.ModelAdmin):
    """Кастомизация админки модели Тэгов."""

    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    """Кастомизация админки модели Ингредиентов."""

    list_display = ('name', 'measurement_unit')
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
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    """Кастомизация админки модели Рецептов."""

    inlines = (IngredientInlineAdmin, TagInlineAdmin,)
    list_display = ('name',
                    'author',
                    'text',
                    'cooking_time',
                    'get_tag',
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

    def get_favorite_counter(self, obj):
        """Позволяет увидеть кол-во добавлений в Избранное."""
        return Favorite.objects.filter(recipe=obj).count()
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
