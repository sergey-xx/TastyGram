import re
import base64
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from rest_framework import serializers
# from rest_framework.serializers import (raise_errors_on_nested_writes,
# traceback)
# from rest_framework.utils import model_meta
from rest_framework.validators import UniqueValidator

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

    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True,
                                     max_length=100,
                                     validators=[UniqueValidator(
                                         queryset=User.objects.all())])
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def create(self, validated_data):
       """Переопределение create для хэширования паролей."""
       validated_data['password'] = make_password(validated_data['password'])
       return super(UserSerializer, self).create(validated_data)

    def validate_email(self, email):
        """Валидация почты."""
        if User.objects.filter(email=email):
            raise serializers.ValidationError('Пользователь с таким email уже '
                                              'существует')
        return email

    def validate_username(self, username):
        """Валидация username."""
        pattern = r'^[\w.@+-]+$'
        if re.search(pattern, username):
            return username
        raise serializers.ValidationError('Имя не может содержать специальные '
                                          'символы')

    def validate_first_name(self, first_name):
        if len(first_name) > 150:
            raise serializers.ValidationError('Имя не может быть длиннее 150 '
                                              'символов')
        return first_name

    def validate_last_name(self, last_name):
        if len(last_name) > 150:
            raise serializers.ValidationError('Имя не может быть длиннее 150 '
                                              'символов')
        return last_name

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
        extra_kwargs = {
                'password': {'write_only': True},
                }


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор Тегов."""

    slug = serializers.SlugField(max_length=200,
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
            pattern = r'^[-a-zA-Z0-9_]'
            if re.search(pattern, slug):
                return slug


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Вспомогательный сериализатор Рецепт/Ингредиент."""

    name = serializers.StringRelatedField(source='ingredient',
                                          read_only=True)
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit',
        read_only=True,)
    amount = serializers.IntegerField()
    id = serializers.PrimaryKeyRelatedField(source='ingredient.id',
                                            queryset=Ingredient.objects.all(),)

    class Meta:
        model = RecipeIngredient
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Вспомогательный сериализатор создания Рецепт/Ингредиент."""

    id = serializers.PrimaryKeyRelatedField(source='ingredient.id',
                                            queryset=Ingredient.objects.all(),
                                            required=True,
                                            )
    amount = serializers.IntegerField(required=True, allow_null=False)
    name = serializers.CharField(source='ingredient.name',
                                 required=False)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        required=False
        )

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


class RecipeAnonymSerializer(serializers.ModelSerializer):
    """Сериалайзер отображения рецептов для Анонимов."""

    ingredients = RecipeIngredientSerializer(source='recipeingredient',
                                             many=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer()

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
    """Сериалайзер отображения Рецепта."""

    ingredients = RecipeIngredientSerializer(source='recipeingredient',
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

    def create(self, validated_data):
        """Кастомная функция создания рецепта."""
        items = validated_data.pop('recipeingredient')
        instance = super().create(validated_data)
        # raise_errors_on_nested_writes('create', self, validated_data)
        # ModelClass = self.Meta.model
        # info = model_meta.get_field_info(ModelClass)
        # many_to_many = {}
        # for field_name, relation_info in info.relations.items():
        #     if relation_info.to_many and (field_name in validated_data):
        #         many_to_many[field_name] = validated_data.pop(field_name)

        # try:
        #     instance = ModelClass._default_manager.create(**validated_data)
        # except TypeError:
        #     tb = traceback.format_exc()
        #     msg = (
        #         'Got a `TypeError` when calling `%s.%s.create()`. '
        #         'This may be because you have a writable field on the '
        #         'serializer class that is not a valid argument to '
        #         '`%s.%s.create()`. You may need to make the field '
        #         'read-only, or override the %s.create() method to handle '
        #         'this correctly.\nOriginal exception was:\n %s' %
        #         (
        #             ModelClass.__name__,
        #             ModelClass._default_manager.name,
        #             ModelClass.__name__,
        #             ModelClass._default_manager.name,
        #             self.__class__.__name__,
        #             tb
        #         )
        #     )
        #     raise TypeError(msg)

        # if many_to_many:
        #     for field_name, value in many_to_many.items():
        #         field = getattr(instance, field_name)
        #         field.set(value)

        for item in items:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=item.get('ingredient').get('id'),
                amount=item['amount'])
        return instance

    def update(self, instance, validated_data):
        if 'recipeingredient' not in validated_data:
            raise serializers.ValidationError(
                'Ингредиенты не могут отсутствовать')
        if 'tags' not in validated_data:
            raise serializers.ValidationError(
                'Тэги не могут отсутствовать')
        items = validated_data.pop('recipeingredient')
        if not items:
            raise serializers.ValidationError(
                'Ингредиенты не могут быть пустыми')
        instance = super().update(instance, validated_data)
        # raise_errors_on_nested_writes('update', self, validated_data)
        # info = model_meta.get_field_info(instance)
        # m2m_fields = []
        # for attr, value in validated_data.items():
        #     if attr in info.relations and info.relations[attr].to_many:
        #         m2m_fields.append((attr, value))
        #     else:
        #         setattr(instance, attr, value)
        # instance.save()
        # for attr, value in m2m_fields:
        #     field = getattr(instance, attr)
        #     field.set(value)

        for item in items:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            for item in items:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=item.get('ingredient').get('id'),
                    amount=item['amount'])

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

        extra_kwargs = {
                'user': {'write_only': True},
                'recipe': {'write_only': True}, }


class FollowSerializer(serializers.ModelSerializer):
    """Сериалайзер добавления Автора в Подписку."""

    username = serializers.StringRelatedField(source='author.username')
    first_name = serializers.StringRelatedField(source='author.first_name')
    last_name = serializers.StringRelatedField(source='author.last_name')
    recipes = RecipeFollowSerializer(read_only=True,
                                     many=True, source='author.recipe')
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
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
        if obj:
            return True

    def get_recipes_count(self, obj):
        recipes_count = Recipe.objects.filter(author=obj.author).count()
        return recipes_count

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        recipes = representation.get('recipes')
        lenth = len(recipes)
        limit = self.context.get('request').query_params.get('recipes_limit')
        if limit:
            limit = int(limit)
            if lenth > limit:
                representation['recipes'] = recipes[:limit]

        return representation


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер Ингредиентов."""

    class Meta:
        fields = ('id',
                  'name',
                  'measurement_unit')
        model = Ingredient


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериалайзер добавления Рецепта в Корзину."""

    # class RecipeFollowSerializer(serializers.ModelSerializer):
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
