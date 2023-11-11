import re
import base64
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.conf import settings


from recipes.models import (Tag, Recipe, RecipeIngredient, Ingredient,
                            Favorite, ShoppingCart, Follow,)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор отображения Пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed'
                  )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        if Follow.objects.filter(follower=user,
                                 author=obj):
            return True
        return False


class UserMeSerializer(UserSerializer):
    """Сериализатор своей страницы."""

    def get_is_subscribed(self, obj):
        return False


class UserCreateSerializer(UserSerializer):
    """Сериализатор создания пользователей."""

    email = serializers.EmailField(required=True,
                                   max_length=settings.MAX_EMAIL_LEN)
    username = serializers.CharField(required=True,
                                     max_length=settings.MAX_USER_LEN,
                                     validators=[UniqueValidator(
                                                 queryset=User.objects.all())])
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def validate_email(self, email):
        """Валидация почты."""
        if User.objects.filter(email=email):
            raise serializers.ValidationError('Пользователь с таким email уже '
                                              'существует')
        return email

    def validate_username(self, username):
        """Валидация username."""
        if re.search(settings.USERNAME_PATTERN, username):
            return username
        raise serializers.ValidationError('Имя не может содержать специальные '
                                          'символы')

    def validate_first_name(self, first_name):
        if len(first_name) > settings.MAX_USER_LEN:
            raise serializers.ValidationError('Имя не может быть длиннее '
                                              f'{settings.MAX_USER_LEN} '
                                              'символов')
        return first_name

    def validate_last_name(self, last_name):
        if len(last_name) > settings.MAX_USER_LEN:
            raise serializers.ValidationError('Имя не может быть длиннее 150 '
                                              'символов')
        return last_name

    def create(self, validated_data):
        """Переопределение create для хэширования паролей."""
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password')
        read_only_fields = ('email',
                            'id',
                            'username',
                            'first_name',
                            'last_name',)
        extra_kwargs = {'password': {'write_only': True}, }


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор Тегов."""

    name = serializers.CharField(max_length=settings.MAX_TAG_LEN,
                                 min_length=1,
                                 allow_blank=False)
    slug = serializers.SlugField(max_length=settings.MAX_TAG_LEN,
                                 min_length=1,
                                 allow_blank=False)

    class Meta:
        fields = ('id',
                  'name',
                  'color',
                  'slug')
        model = Tag

        def validate_slug(self, slug):
            """Валидация поля Slug."""
            if re.search(settings.TAG_SLUG_PATTERN, slug):
                return slug

        def validate_color(self, color):
            """Валидация поля Color."""
            pattern = r'#[A-F0-9_]{6}'
            if re.search(pattern, color):
                return color


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Вспомогательный сериализатор создания Рецепт/Ингредиент."""

    id = serializers.PrimaryKeyRelatedField(source='ingredient.id',
                                            queryset=Ingredient.objects.all(),
                                            required=True,
                                            )
    name = serializers.CharField(source='ingredient.name',
                                 required=False)
    amount = serializers.IntegerField(required=True,
                                      allow_null=False,)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        required=False)

    class Meta:
        model = RecipeIngredient
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount')

    def validate_amount(self, amount):
        """Валидация Количества Ингредиента."""
        if amount < 1:
            raise serializers.ValidationError(
                'Количество не может быть менее 1')
        return amount


class Base64ImageField(serializers.ImageField):
    """Сериализатор картинок в HEX."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер отображения Рецепта."""

    ingredients = RecipeIngredientCreateSerializer(source='recipeingredient',
                                                   many=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer()

    class Meta:
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time',
                  )
        read_only_fields = ('author',)
        model = Recipe

    def get_is_favorited(self, obj):
        """Получение нахождения в Любимых."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        favorite = Favorite.objects.filter(user=user, recipe=obj)
        return favorite.exists()

    def get_is_in_shopping_cart(self, obj):
        """Получение нахождения в Корзине."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        favorite = ShoppingCart.objects.filter(user=user, recipe=obj)
        return favorite.exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер создания Рецепта."""

    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = RecipeIngredientCreateSerializer(source='recipeingredient',
                                                   many=True,
                                                   required=True,
                                                   allow_null=False,)
    image = Base64ImageField(required=True, allow_null=False)
    author = UserSerializer(required=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')
        read_only_fields = ('id', 'author')
        model = Recipe

    def validate_ingredients(self, ingredients):
        """Валидация ингредиентов."""
        unique = set()
        for ingredient in ingredients:
            if ingredient.get('ingredient').get('id').id in unique:
                raise serializers.ValidationError('Ингредиенты не могут '
                                                  'повторяться')
            unique.add(ingredient.get('ingredient').get('id').id)
        if not ingredients:
            raise serializers.ValidationError(
                'Ингредиенты не могут отсутствовать')
        return ingredients

    def validate_tags(self, tags):
        """Валидация Тэгов."""
        unique = set()
        for tag in tags:
            if tag.id in unique:
                raise serializers.ValidationError('tag не могут повторяться')
            unique.add(tag.id)
        if not tags:
            raise serializers.ValidationError(
                'Тэги не могут отсутствовать')
        return tags

    def validate(self, attrs):
        if 'tags' not in attrs:
            raise serializers.ValidationError(
                'Тэги не могут отсутствовать')

        if 'recipeingredient' not in attrs:
            raise serializers.ValidationError(
                'Ингредиенты не могут отсутствовать')
        return attrs

    def get_is_favorited(self, obj):
        """Получение нахождения в Любимых."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        favorite = Favorite.objects.filter(user=user, recipe=obj)
        return favorite.exists()

    def get_is_in_shopping_cart(self, obj):
        """Получение нахождения в Корзине."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        favorite = ShoppingCart.objects.filter(user=user, recipe=obj)
        return favorite.exists()

    def create_ingredient(self, items, instance):
        ingredients = []
        for item in items:
            ingredients.append(
                RecipeIngredient(recipe=instance,
                                 ingredient=item.get('ingredient').get('id'),
                                 amount=item['amount']))
        RecipeIngredient.objects.bulk_create(ingredients)

    def create(self, validated_data):
        """Кастомная функция создания рецепта."""
        items = validated_data.pop('recipeingredient')
        instance = super().create(validated_data)
        self.create_ingredient(items, instance)
        return instance

    def update(self, instance, validated_data):
        items = validated_data.pop('recipeingredient')
        # if not items:
        #     raise serializers.ValidationError(
        #         'Ингредиенты не могут быть пустыми')
        RecipeIngredient.objects.filter(recipe=instance).delete()
        instance = super().update(instance, validated_data)
        self.create_ingredient(items, instance)
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags,
            many=True,).data
        return representation


class RecipeFollowSerializer(serializers.ModelSerializer):
    """Сериалайзер добавления связки Рецепт/Подписка."""

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time'
                  )
        model = Recipe


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер добавления Рецепта в Любимые."""

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

        extra_kwargs = {'user': {'write_only': True},
                        'recipe': {'write_only': True}, }

    def validate(self, attrs):
        recipe_id = self.context.get(
            'request').parser_context.get('kwargs').get('title_id')
        recipe = Recipe.objects.filter(id=recipe_id)
        if not recipe.exists():
            raise serializers.ValidationError('Рецепт не существует')
        user = self.context.get('request').user
        is_exists = Favorite.objects.filter(user=user,
                                            recipe=int(recipe_id)).exists()
        if is_exists:
            raise serializers.ValidationError('Рецепт уже в избранном')
        return attrs


class FollowSerializer(serializers.ModelSerializer):
    """Сериалайзер добавления Автора в Подписку."""

    id = serializers.PrimaryKeyRelatedField(source='author',
                                            read_only=True)
    username = serializers.StringRelatedField(source='author.username')
    first_name = serializers.StringRelatedField(source='author.first_name')
    last_name = serializers.StringRelatedField(source='author.last_name')
    recipes = RecipeFollowSerializer(read_only=True,
                                     many=True, source='author.recipe')
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)
    email = serializers.StringRelatedField(source='author.email')

    class Meta:
        fields = ('id',
                  'username',
                  'first_name',
                  'last_name',
                  'email',
                  'is_subscribed',
                  'recipes_count',
                  'recipes',)

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
        if Follow.objects.filter(follower=self.context.get('request').user,
                                 author=obj.author).exists():
            return True
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        recipes = representation.get('recipes')
        length = len(recipes)
        representation['recipes_count'] = length
        limit = self.context.get('request').query_params.get('recipes_limit')
        if limit:
            limit = int(limit)
            if length > limit:
                representation['recipes'] = recipes[:limit]
        return representation

    def validate(self, attrs):
        author_id = int(self.context.get(
            'request').parser_context.get('kwargs').get('title_id'))
        user_id = self.context.get('request').user.id
        if author_id == user_id:
            raise serializers.ValidationError('Нельзя подписаться на самого '
                                              'себя')
        if Follow.objects.filter(follower=user_id,
                                 author=author_id).exists():
            raise serializers.ValidationError('Вы уже подписаны')
        return attrs


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер Ингредиентов."""

    class Meta:
        fields = ('id',
                  'name',
                  'measurement_unit')
        model = Ingredient


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериалайзер добавления Рецепта в Корзину."""

    id = serializers.PrimaryKeyRelatedField(source='recipe', read_only=True)
    name = serializers.StringRelatedField(source='recipe.name', read_only=True)
    cooking_time = serializers.IntegerField(source='recipe.cooking_time',
                                            required=False,
                                            read_only=True)
    image = Base64ImageField(source='recipe.image',
                             required=False,
                             allow_null=True)

    class Meta:
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time'
                  )
        read_only_fields = ('id',
                            'name',
                            'image',
                            'cooking_time'
                            )
        model = ShoppingCart

    def validate(self, attrs):
        recipe_id = self.context.get(
            'request').parser_context.get('kwargs').get('title_id')
        recipes = Recipe.objects.filter(id=recipe_id)
        if not recipes.exists():
            raise serializers.ValidationError('Рецепт не существует')
        user = self.context.get('request').user
        recipe = recipes.first()
        if ShoppingCart.objects.filter(user=user,
                                       recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже в корзине')
        return attrs
