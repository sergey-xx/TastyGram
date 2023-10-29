from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes


from recipes.models import Tag, Recipe, RecipeIngredient, Favorite
from .serializers import (UserSerializer, TagSerializer, RecipeSerializer,
                          RecipeIngredientSerializer, RecipeCreateSerializer,
                          FavoriteSerializer, RecipeAnonymSerializer)

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


class UserMe(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.get(request)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов"""
    queryset = Recipe.objects.all().order_by('id')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            return RecipeAnonymSerializer
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
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
    # def set_password(self, request, pk=None):
    def delete(self, request, *args, **kwargs):
        title_id = kwargs.get('title_id')
        recipe = get_object_or_404(Recipe, id=title_id)
        print(title_id)
        favorite = Favorite.objects.filter(recipe=title_id, user=self.request.user)
        if favorite.exists():
            favorite[0].delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
        
