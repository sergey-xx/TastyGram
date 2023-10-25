from rest_framework import serializers
from django.utils import timezone
import re
from django.contrib.auth import get_user_model

from recipes.models import Tag

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):


    class Meta:
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  )
        
        model = User

class UserCreateSerializer(UserSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate_email(self, email):
        if User.objects.filter(email=email):
            raise serializers.ValidationError('Пользователь с таким email уже существует')
        return email

    def validate_username(self, username):
        pattern = r'^[\w.@+-]+$'
        if re.search(pattern, username):
            return username
        raise serializers.ValidationError(
            'Имя не может содержать специальные символы')

    class Meta:
        fields = ('email',
                  'username',
                  'first_name',
                  'last_name',
                  'password'
                  )
        model = User


class TagSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(max_length=200, min_length=1, allow_blank=False)
    class Meta:
        fields = ('id',
                  'name',
                  'color',
                  'slug')
        model = Tag
        # lookup_field = 'slug'

        def validate_slug(self, slug):
            pattern = r'^[-a-zA-Z0-9_]'
            if re.search(pattern, slug):
                return slug