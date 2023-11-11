from django.db.models import Count
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView

from core.pagination import CustomPagination
from recipes.models import (Tag, Recipe, Favorite, Follow,
                            Ingredient, ShoppingCart)
from .serializers import (UserSerializer, TagSerializer, RecipeSerializer,
                          RecipeCreateSerializer, UserMeSerializer,
                          FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, ShoppingCartSerializer)
from .permissions import IsOwnerOrReadOnly
from .filters import RecipeFilter, IngredientFilter

User = get_user_model()


class UsersViewSet(mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    """ViewSet для просмотра и редактирования данных пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny, )
    http_method_names = ['get', 'post']
    pagination_class = CustomPagination


class UserMe(APIView):
    """Вьюсет для своей страницы."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        serializer = UserMeSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.get(request)


class TagsViewSet(viewsets.ModelViewSet):
    """Вьюсет для Тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'id'
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)
    http_method_names = ['get']
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all().order_by('-pub_date')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            return RecipeSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class BaseViewset(viewsets.ModelViewSet):
    """Базовая модель для Подписки, Любимых, Корзины."""

    def _get_title_id(self):
        return self.kwargs.get('title_id')

    def _get_title(self, title_model):
        return get_object_or_404(title_model, id=self._get_title_id())

    def perform_create(self, serializer):
        recipe = self._get_title(self.title_model)
        serializer.save(user=self.request.user,
                        recipe=recipe,)

    @action(methods=['delete'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def delete(self, request, *args, **kwargs):
        recipe = self._get_title(self.title_model)
        model_items = self.model.objects.filter(recipe=recipe,
                                                user=self.request.user)
        if model_items.exists():
            model_items.first().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Объект не существует.',
                        status=status.HTTP_400_BAD_REQUEST)


class FavoriteViewSet(BaseViewset):
    """Вьюсет добавления в Любимые."""

    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    model = Favorite
    title_model = Recipe
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post', 'delete']
    lookup_field = 'id'
    pagination_class = CustomPagination


class ShoppingCartViewSet(BaseViewset):
    """Вьюсет добавления в Корзину."""

    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post', 'delete']
    pagination_class = CustomPagination
    model = ShoppingCart
    title_model = Recipe


class FollowViewSet(BaseViewset):
    """Вьюсет добавления в Подписки."""

    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post', 'delete']
    model = Follow
    title_model = User

    def perform_create(self, serializer):
        author = self._get_title(self.title_model)
        serializer.save(follower=self.request.user,
                        author=author,)

    @action(methods=['delete'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def delete(self, request, *args, **kwargs):
        author = self._get_title(self.title_model)
        model_items = self.model.objects.filter(author=author,
                                                follower=self.request.user)
        if model_items.exists():
            model_items.first().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Объект не существует.',
                        status=status.HTTP_400_BAD_REQUEST)


class FollowListViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """Вьюсет просмотра списка Подписок."""

    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = (
            Follow.objects.annotate(recipes_count=Count('author__recipe')))
        return queryset.filter(follower=self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет просмотра Ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    filterset_fields = ('name',)
