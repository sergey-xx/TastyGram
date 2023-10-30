from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter

from .views import (UserMe, TagsViewSet, RecipeViewSet, FavoriteViewSet,
                    FollowViewSet, FollowListViewSet)

router = DefaultRouter()
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
# router.register(r'(?P<title_id>\d+)/favorite', FavoriteViewSet, basename='favorite')
router.register(r'recipes/(?P<title_id>\d+)/favorite', FavoriteViewSet, basename='favorite-detail')
router.register(r'users/(?P<title_id>\d+)/subscribe', FollowViewSet, basename='Follow-detail')
router.register('users/subscriptions', FollowListViewSet, basename='Follow')


urlpatterns = [
    path('users/me/', UserMe.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls),),
    path('', include('djoser.urls')),
]
