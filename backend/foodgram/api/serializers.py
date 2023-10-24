from rest_framework import serializers
from django.utils import timezone
import re

from django.contrib.auth import get_user_model

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

    def validate_username(self, username):

        pattern = r'^[\w.@+-]+$'
        if username != 'me' and re.search(pattern, username):
            return username
        raise serializers.ValidationError(
            'Имя не может содержать специальные символы и не равно "me"')


class UserCreateSerializer(UserSerializer):

    class Meta:
        fields = ('email',
                  'username',
                  'first_name',
                  'last_name',
                  'password'
                  )
        model = User


class UserPathSerializer(UserSerializer):

    class Meta:
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  )
        model = User
