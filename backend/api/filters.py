import django_filters

from recipes.models import Recipe
from django.db import models



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

    def filter_queryset(self, queryset):
        for name, value in self.form.cleaned_data.items():
            queryset = self.filters[name].filter(queryset, value)
            assert isinstance(
                queryset, models.QuerySet
            ), "Expected '%s.%s' to return a QuerySet, but got a %s instead." % (
                type(self).__name__,
                name,
                type(queryset).__name__,
            )
        if self.request.query_params.get('is_favorited') == '1':
            return Recipe.objects.filter(favorite__user=self.request.user)
        if self.request.query_params.get('is_in_shopping_cart') == '1':
            return Recipe.objects.filter(shoppingcart__user=self.request.user)
        return queryset