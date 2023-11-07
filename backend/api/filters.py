import django_filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """
    Фильтр для запросов к объектам модели Recipe.
    Фильтрация осуществляется по slug тэга,.
    """
    tags = django_filters.CharFilter(
        field_name='tags__slug', lookup_expr='iexact'
    )
    author = django_filters.CharFilter(
        field_name='author__id', lookup_expr='iexact'
    )
    shoppingcart = django_filters.BooleanFilter(
        field_name='is_in_shopping_cart__id', lookup_expr='isnull'
    )
    favorited = django_filters.BooleanFilter(
        field_name='is_favorited__id', lookup_expr='isnull'
    )
    class Meta:
        model = Recipe
        fields = ('tags', 'is_in_shopping_cart', 'is_favorited')
