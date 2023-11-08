import os
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)


from recipes.models import (Tag, Recipe, RecipeIngredient, Favorite, Follow,
                            Ingredient, ShoppingCart)
from .serializers import (UserSerializer, TagSerializer, RecipeSerializer,
                          RecipeCreateSerializer, UserMeSerializer,
                          FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, ShoppingCartSerializer)
from .permissions import IsOwnerOrReadOnly
from .filters import RecipeFilter

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
    pagination_class = LimitOffsetPagination


class UserMe(APIView):
    """Вьюсет для своей страницы."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        serializer = UserMeSerializer(user)
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

    queryset = Recipe.objects.all().order_by('id')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)
    pagination_class = LimitOffsetPagination
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


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет добавления в избранные."""

    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post', 'delete']
    lookup_field = 'id'
    pagination_class = PageNumberPagination

    def _get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Recipe, id=title_id)

    def create(self, request, *args, **kwargs):
        title_id = self.kwargs.get('title_id')
        titles = Recipe.objects.filter(id=title_id)
        if not titles.exists():
            raise serializers.ValidationError('Рецепт не существует')
        recipe = self._get_title()
        result = Favorite.objects.filter(user=self.request.user,
                                         recipe=recipe).exists()
        if result:
            raise serializers.ValidationError('Рецепт уже в избранном')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        recipe = self._get_title()
        serializer.save(user=self.request.user,
                        recipe=recipe,)

    @action(methods=['delete'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def delete(self, request, *args, **kwargs):
        title_id = self.kwargs.get('title_id')
        titles = Recipe.objects.filter(id=title_id)
        get_object_or_404(Recipe, id=title_id)
        if not titles.exists():
            raise serializers.ValidationError('Рецепт не существует')
        title_id = kwargs.get('title_id')
        favorite = Favorite.objects.filter(recipe=title_id,
                                           user=self.request.user)
        if favorite.exists():
            favorite[0].delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class FollowViewSet(viewsets.ModelViewSet):
    """Вьюсет добавления и просмотра Подписки."""

    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post', 'delete']

    def _get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(User, id=title_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        author = self._get_title()
        if author == self.request.user:
            raise serializers.ValidationError('Нельзя подписаться на самого '
                                              'себя!')
        if Follow.objects.filter(follower=self.request.user,
                                 author=author).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        author = self._get_title()
        serializer.save(follower=self.request.user,
                        author=author,)

    @action(methods=['delete'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def delete(self, request, *args, **kwargs):
        author = kwargs.get('title_id')
        get_object_or_404(User,
                          id=author)
        follow = Follow.objects.filter(author=author,
                                       follower=self.request.user)
        if not follow.exists():
            raise serializers.ValidationError('Вы не были подписаны!')
        follow = get_object_or_404(Follow,
                                   author=author,
                                   follower=self.request.user)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowListViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """Вьюсет просмотра списка Подписок."""

    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Follow.objects.filter(follower=self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет просмотра Ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Вьюсет добавления и просмотра Корзины."""

    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post', 'delete']
    pagination_class = PageNumberPagination

    def _get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Recipe, id=title_id)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        titles = Recipe.objects.filter(id=title_id)
        if not titles.exists():
            raise serializers.ValidationError('Рецепт не существует')
        recipe = self._get_title()
        if ShoppingCart.objects.filter(user=self.request.user,
                                       recipe=recipe).count() > 0:
            raise serializers.ValidationError('Рецепт уже в корзине')
        serializer.save(user=self.request.user,
                        recipe=recipe,)

    @action(methods=['delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def delete(self, request, *args, **kwargs):
        title_id = self.kwargs.get('title_id')
        recipe = get_object_or_404(Recipe, id=title_id)
        title_id = self.kwargs.get('title_id')
        titles = Recipe.objects.filter(id=title_id)
        if not titles.exists():
            raise serializers.ValidationError('Рецепт не существует')
        if ShoppingCart.objects.filter(recipe=recipe,
                                       user=self.request.user).count() < 1:
            raise serializers.ValidationError('Рецепт не был ранее добавлен '
                                              'в корзину')
        shopping_cart = get_object_or_404(ShoppingCart,
                                          recipe=recipe,
                                          user=self.request.user)
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadViewSet(APIView):
    """Вьюсет для скачивания списка покупок."""

    permission_classes = (AllowAny,)

    def merge_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = []
        for item in shopping_cart:
            recipes.append(item.recipe)

        items = dict()
        for recipe in recipes:
            recipeingredients = RecipeIngredient.objects.filter(recipe=recipe)
            for recipeingredient in recipeingredients:
                name = recipeingredient.ingredient.name
                amount = recipeingredient.amount
                if name in items:
                    items[name] += amount
                else:
                    items[name] = amount
        return items

    def get(self, request):
        items = self.merge_shopping_cart(request)

        if os.path.exists('shopping_cart.txt'):
            os.remove('shopping_cart.txt')

        with open('shopping_cart.txt', 'x') as file:
            for key, item in items.items():
                file.write(key + '\t' + str(item) + '\n')

        with open('shopping_cart.txt', 'r') as file:
            response = HttpResponse(file, content_type='text/csv',
                                    status=status.HTTP_200_OK)
            response['Content-Disposition'] = ('attachment; '
                                               'filename=shopping_cart.txt')

        if os.path.exists('shopping_cart.txt'):
            os.remove('shopping_cart.txt')
        return response
