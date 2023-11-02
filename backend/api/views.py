import os
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import viewsets, mixins, status, renderers
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers


from recipes.models import (Tag, Recipe, RecipeIngredient, Favorite, Follow,
                            Ingredient, ShoppingCart)
from .serializers import (UserSerializer, TagSerializer, RecipeSerializer,
                          RecipeCreateSerializer, UserMeSerializer,
                          FavoriteSerializer, RecipeAnonymSerializer,
                          FollowSerializer, IngredientSerializer)
from .permissions import IsOwnerOrReadOnly

User = get_user_model()


class UsersViewSet(mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    """ViewSet для просмотра пользователей и редактирования
    данных пользователя."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny, )
    http_method_names = ['get', 'post']


class UserMe(APIView):
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
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'id'
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)
    http_method_names = ['get']



class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов"""
    queryset = Recipe.objects.all().order_by('id')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            # return RecipeAnonymSerializer
            return RecipeSerializer
        if self.action == 'create' or self.action == 'update':
            return RecipeCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post','delete']
    lookup_field = 'id'


    def _get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Recipe, id=title_id)

    def create(self, request, *args, **kwargs):
        recipe = self._get_title()
        result = Favorite.objects.filter(user=self.request.user, recipe=recipe).exists()
        if result:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        recipe = self._get_title()
        serializer.save(user=self.request.user,
                               recipe=recipe,)


    @action(methods=['delete'], detail=True, permission_classes=[IsAuthenticated])
    def delete(self, request, *args, **kwargs):
        title_id = kwargs.get('title_id')
        recipe = get_object_or_404(Recipe, id=title_id)
        favorite = Favorite.objects.filter(recipe=title_id, user=self.request.user)
        if favorite.exists():
            favorite[0].delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post','delete']

    def _get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(User, id=title_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        author = self._get_title()
        print(self.request.user)
        print(author)
        if author == self.request.user:
            raise serializers.ValidationError('Нельзя подписаться на самого сетя!')
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

    @action(methods=['delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def delete(self, request, *args, **kwargs):
        title_id = kwargs.get('title_id')
        follow = Follow.objects.filter(author=title_id,
                                       follower=self.request.user)
        if follow.exists():
            follow[0].delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class FollowListViewSet(mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        return Follow.objects.filter(follower=self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    http_method_names = ['get']


class DownloadViewSet(APIView):
    permission_classes = (AllowAny,)

    def merge_shopping_cart(self, request):
    # shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        shopping_cart = ShoppingCart.objects.filter(user=1)
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
