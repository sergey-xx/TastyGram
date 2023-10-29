from django.db import models
from django.contrib.auth import get_user_model

from .validators import time_validator

User = get_user_model()


class Tag(models.Model):
    """Класс Тегов"""
    name = models.CharField('Имя', max_length=200, unique=True, blank=False)
    color = models.CharField('Цвет', max_length=7, null=True, default=None)
    slug = models.SlugField('Slug', max_length=200, unique=True)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):
    """Класс Ингредиентов"""
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единица измерения',
                                        max_length=200)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    """Класс Рецептов"""
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='recipe',)
    tags = models.ManyToManyField(Tag,
                                  blank=True,
                                  related_name='recipe',
                                  verbose_name='Теги')
    image = models.ImageField('Картинка', )
    name = models.CharField('Название',
                            max_length=200)
    text = models.TextField('Рецепт', )
    cooking_time = models.IntegerField('Время приготовления, мин',
                                       validators=[time_validator, ])
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',)
    is_favorited = models.ManyToManyField(User,
                                          through='Favorite',
                                          related_name='recipes')
    is_in_shopping_cart = models.ManyToManyField(User,
                                          through='ShoppingCart',
                                          related_name='products'
                                          )

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    """Класс связи рецептов с ингредиентами"""
    amount = models.IntegerField()
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   blank=False,
                                   verbose_name='Ингредиент',
                                   related_name='recipeingredient')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               blank=False,
                               verbose_name='Рецепт',
                               related_name='recipeingredient')

    def __str__(self) -> str:
        return str(self.ingredient) + str(self.recipe) + str(self.amount)

    class Meta:
        verbose_name = 'Ингредиент/рецепт'
        verbose_name_plural = 'Ингредиенты/рецепты'


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             blank=True,
                             related_name='favorite',
                             )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               blank=True,
                               related_name='favorite',
                               )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite'
        )]
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые'

    def __str__(self) -> str:
        return str(self.user) + '/' + str(self.recipe)
    


class ShoppingCart(models.Model):
    """Добавление рецепта в корзину"""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shoppingcart')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='shoppingcart')

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping_card'
        )]
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self) -> str:
        return str(self.user) + '/' + str(self.recipe)


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')


    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['follower', 'author'],
            name='unique_following'
        )]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return str(self.follower) + '/' + str(self.author)