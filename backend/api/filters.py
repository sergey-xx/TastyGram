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
        """
        Для проверки нахождения в Корзине и в Любимых.

        Queryset генерируется из БД.
        """
        if self.request.query_params.get('is_favorited') == '1':
            if self.request.user.is_anonymous:
                return Recipe.objects.all()
            return Recipe.objects.filter(favorite__user=self.request.user)
        if self.request.query_params.get('is_in_shopping_cart') == '1':
            if self.request.user.is_anonymous:
                return Recipe.objects.all()
            return Recipe.objects.filter(shoppingcart__user=self.request.user)
        return super().filter_queryset(queryset)
