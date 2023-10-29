from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter

from .views import (UserMe, TagsViewSet, RecipeViewSet, FavoriteViewSet
                     )

router = DefaultRouter()
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
# router.register(r'(?P<title_id>\d+)/favorite', FavoriteViewSet, basename='favorite')
router.register(r'recipes/(?P<title_id>\d+)/favorite', FavoriteViewSet, basename='favorite-detail')
urlpatterns = [
    path('users/me/', UserMe.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(router.urls),),
]
