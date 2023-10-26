from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter

from .views import (UserMe, TagsViewSet, RecipeViewSet,
                     )

router = DefaultRouter()
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('users/me/', UserMe.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(router.urls),),
]
