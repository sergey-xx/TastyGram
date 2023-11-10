import django_filters
from django_filters.widgets import BooleanWidget

from recipes.models import Recipe, Ingredient


class RecipeFilter(django_filters.FilterSet):
    """
    Фильтр для запросов к объектам модели Recipe.

    Фильтрация осуществляется по slug тэга, id автора
    нахождении в любимых и в корзине пользователя.
    """

    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug', lookup_expr='iexact')

    is_in_shopping_cart = django_filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart',
        widget=BooleanWidget())

    is_favorited = django_filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited',
        widget=BooleanWidget())

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        return queryset.filter(shoppingcart__user=self.request.user)

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        return queryset.filter(favorite__user=self.request.user)

    class Meta:
        model = Recipe
        fields = ('tags', 'is_in_shopping_cart', 'is_favorited', 'author')


class IngredientFilter(django_filters.FilterSet):
    """Для фильтрации по Ингредиентам."""

    name = django_filters.CharFilter(
        field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
