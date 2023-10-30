import re
import base64
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes, traceback
from rest_framework.utils import model_meta
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from collections import OrderedDict

from recipes.models import (Tag, Recipe, RecipeIngredient, Ingredient, Favorite,
                            ShoppingCart, Follow)

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

        def validate_slug(self, slug):
            pattern = r'^[-a-zA-Z0-9_]'
            if re.search(pattern, slug):
                return slug


class TagRecipeCrateSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id',)
        model = Tag


class RecipeIngredientSerializer(serializers.ModelSerializer):

    name = serializers.StringRelatedField(source='ingredient', read_only=True)
    measurement_unit = serializers.StringRelatedField(source='ingredient.measurement_unit',
                                                      read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id',
                  'amount')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeAnonymSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(source='recipeingredient',
                                              many=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'image',
                  'name',
                  'text',
                  )
        model = Recipe


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(source='recipeingredient',
                                              many=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'image',
                  'name',
                  'text',
                  'is_favorited',
                  'is_in_shopping_cart',
                  )
        model = Recipe

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        favorite = Favorite.objects.filter(user=user, recipe=obj)
        return favorite.exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        favorite = ShoppingCart.objects.filter(user=user, recipe=obj)
        return favorite.exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = RecipeIngredientCreateSerializer(source='recipeingredient',
                                                  many=True, )
    image = Base64ImageField(required=False, allow_null=True)
    
    def create(self, validated_data):
        items = validated_data.pop('recipeingredient')
        raise_errors_on_nested_writes('create', self, validated_data)
        ModelClass = self.Meta.model
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = ModelClass._default_manager.create(**validated_data)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                'Got a `TypeError` when calling `%s.%s.create()`. '
                'This may be because you have a writable field on the '
                'serializer class that is not a valid argument to '
                '`%s.%s.create()`. You may need to make the field '
                'read-only, or override the %s.create() method to handle '
                'this correctly.\nOriginal exception was:\n %s' %
                (
                    ModelClass.__name__,
                    ModelClass._default_manager.name,
                    ModelClass.__name__,
                    ModelClass._default_manager.name,
                    self.__class__.__name__,
                    tb
                )
            )
            raise TypeError(msg)

        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(instance, field_name)
                field.set(value)

        for item in items:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            RecipeIngredient.objects.create(recipe=instance,
                                            ingredient=ingredient,
                                            amount=item['amount'])
        return instance

    class Meta:
        fields = ('tags',
                  'ingredients',
                  'image',
                  'name',
                  'text',
                  'cooking_time')
        model = Recipe


class RecipeFollowSerializer(serializers.ModelSerializer):

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time'
                  )
        model = Recipe


class FavoriteSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source='recipe.name')
    cooking_time = serializers.IntegerField(source='recipe.cooking_time',
                                            read_only=True)
    image = Base64ImageField(required=False,
                             allow_null=True,
                             source='recipe.image')

    class Meta:
        fields = ('user', 'recipe', 'id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
        model = Favorite

        extra_kwargs = {
                'user': {'write_only': True},
                'recipe': {'write_only': True},}


class FollowSerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(source='author.username')
    first_name = serializers.StringRelatedField(source='author.first_name')
    last_name = serializers.StringRelatedField(source='author.last_name')
    recipes = RecipeFollowSerializer(read_only=True, many=True, source='author.recipe')
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    email = serializers.StringRelatedField(source='author.email')

    class Meta:
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')

        read_only_fields = ('email',
                            'id',
                            'username',
                            'first_name',
                            'last_name',
                            'is_subscribed',
                            'recipes',
                            'recipes_count',)

        model = Follow

    def get_is_subscribed(self, obj):
        if obj:
            return True

    def get_recipes_count(self, obj):
        recipes_count = Recipe.objects.filter(author=obj.author).count()
        return recipes_count

class FollowListSerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(source='author.username')
    first_name = serializers.StringRelatedField(source='author.first_name')
    last_name = serializers.StringRelatedField(source='author.last_name')
    recipes = RecipeFollowSerializer(read_only=True, many=True, source='author.recipe')
    # is_subscribed = serializers.SerializerMethodField()
    # recipes_count = serializers.SerializerMethodField()
    email = serializers.StringRelatedField(source='author.email')

    class Meta:
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                #   'is_subscribed',
                  'recipes',
                #   'recipes_count'
                  )

        read_only_fields = ('email',
                            'id',
                            'username',
                            'first_name',
                            'last_name',
                            # 'is_subscribed',
                            'recipes',
                            # 'recipes_count',
                            )

        model = Follow