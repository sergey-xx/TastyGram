import django_filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """
    Фильтр для запросов к объектам модели Recipe.

    Фильтрация осуществляется по slug тэга, id автора
    нахождении в любимых и в корзине пользователя.
    """

    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug', lookup_expr='iexact'
    )
    author = django_filters.CharFilter(
        field_name='author__id', lookup_expr='iexact'
    )
    is_in_shopping_cart = django_filters.Filter(
        field_name='is_in_shopping_cart'
    )
    is_favorited = django_filters.Filter(
        field_name='is_favorited'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'is_in_shopping_cart', 'is_favorited')

    def filter_queryset(self, queryset):
        """Для проверки нахождения в Корзине и в Любимых."""
        is_favorited = self.form.cleaned_data.pop('is_favorited')
        is_in_shopping_cart = self.form.cleaned_data.pop('is_in_shopping_cart')
        if not self.request.user.is_anonymous:
            if is_favorited and is_favorited != '0':
                queryset = queryset.filter(favorite__user=self.request.user)
            if is_in_shopping_cart and is_in_shopping_cart != '0':
                queryset = queryset.filter(
                    shoppingcart__user=self.request.user)

        return super().filter_queryset(queryset)
