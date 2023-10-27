from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes


from recipes.models import Tag, Recipe, RecipeIngredient, Favorite
from .serializers import (UserSerializer, TagSerializer, RecipeSerializer,
                          RecipeIngredientSerializer, RecipeCreateSerializer,
                          FavoriteSerializer)

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
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def _get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Recipe, id=title_id)

    def perform_create(self, serializer):
        recipe = Recipe.objects.get(id=1)
        print(f'>>>>>>>>>>>>>> {recipe}')
        # recipe = self._get_title()
        # favorite = Favorite.objects.create(user=self.request.user,
        #                                    recipe=recipe)
        return serializer.save(user=self.request.user,
                               recipe=recipe)

    # def get_queryset(self):
    #     return Favorite.objects.filter(user=self.request.user)
