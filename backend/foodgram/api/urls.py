from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter

from .views import UsersViewSet, UserMe

router = DefaultRouter()
# router.register('users', UsersViewSet, basename='user')



urlpatterns = [
    path('users/me/', UserMe.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    # path('auth/token/login/', create_token, name='login'),
    # path('auth/token/logout/', delete_token, name='logout'),
    # path('', include(router.urls),),
]
