from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (UserMe, TagsViewSet, RecipeViewSet,
                    FavoriteViewSet,
                    FollowViewSet,
                    FollowListViewSet,
                    IngredientViewSet,
                    ShoppingCartViewSet)
from .utils import DownloadViewSet

router = DefaultRouter()
router.register('tags',
                TagsViewSet,
                basename='tags')

router.register('recipes',
                RecipeViewSet,
                basename='recipes')

router.register(r'recipes/(?P<title_id>\d+)/favorite',
                FavoriteViewSet,
                basename='favorite-detail')

router.register(r'users/(?P<title_id>\d+)/subscribe',
                FollowViewSet,
                basename='follow-detail')

router.register(r'recipes/(?P<title_id>\d+)/shopping_cart',
                ShoppingCartViewSet,
                basename='shopping_cart')

router.register('users/subscriptions',
                FollowListViewSet,
                basename='follow-list')

router.register('ingredients',
                IngredientViewSet,
                basename='Ingredient')

urlpatterns = [
    path('users/me/', UserMe.as_view()),
    path('auth/', include('djoser.urls.authtoken')),

    path('recipes/download_shopping_cart/',
         DownloadViewSet.as_view(),
         name='shopping_card'),

    path('', include(router.urls),),
    path('', include('djoser.urls')),
]
