from django.contrib.auth import get_user_model
from django.db import models

from .validators import amount_validator, time_validator

User = get_user_model()


class Tag(models.Model):
    """Класс Тегов."""

    name = models.CharField('Имя', max_length=200, unique=True, blank=False)
    color = models.CharField('Цвет', max_length=7, null=True, default=None)
    slug = models.SlugField('Slug', max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        """Отобращает название в виде имени."""
        return self.name


class Ingredient(models.Model):
    """Класс Ингредиентов."""

    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единица измерения',
                                        max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        """Отобращает название в виде имени."""
        return self.name


class Recipe(models.Model):
    """Класс Рецептов."""

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='recipe',)
    tags = models.ManyToManyField(Tag,
                                  through='RecipeTag',)
    image = models.ImageField('Картинка', )
    name = models.CharField('Название',
                            max_length=200)
    text = models.TextField('Рецепт', )
    cooking_time = models.IntegerField('Время приготовления, мин',
                                       validators=[time_validator, ])
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         blank=False,)
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        """Отобращает название в виде поля имя."""
        return self.name


class RecipeTag(models.Model):
    """Связь Тэгов и Рецептов."""

    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            blank=False,
                            verbose_name='тэг',
                            related_name='recipetag')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               blank=False,
                               verbose_name='Рецепт',
                               related_name='recipetag')

    class Meta:
        verbose_name = 'Рецепт/тег'
        verbose_name_plural = 'Рецепты/теги'
        constraints = [models.UniqueConstraint(
            fields=['tag', 'recipe'],
            name='unique_recipe_tag'
        )]

    def __str__(self) -> str:
        """Отобращает название в виде Рецепт/Тэг."""
        return f'{self.recipe} / {self.tag}'


class RecipeIngredient(models.Model):
    """Класс связи рецептов с ингредиентами."""

    amount = models.IntegerField('Количество',
                                 validators=[amount_validator, ])
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

    class Meta:
        verbose_name = 'Ингредиент/рецепт'
        verbose_name_plural = 'Ингредиенты/рецепты'
        constraints = [models.UniqueConstraint(
            fields=['ingredient', 'recipe'],
            name='unique_recipe_ingredient'
        )]

    def __str__(self) -> str:
        """Отобращает название в виде Ингредиент/Рецепт/Количество."""
        return (str(self.ingredient) + '/'
                + str(self.recipe) + '/' + str(self.amount))


class Favorite(models.Model):
    """Добавление рецептов в Избранное."""

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
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранное'

    def __str__(self) -> str:
        """Отобращает название в виде Пользователь/Рецепт."""
        return str(self.user) + '/' + str(self.recipe)


class ShoppingCart(models.Model):
    """Добавление рецепта в Список покупок."""

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
        verbose_name = 'В Списке покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self) -> str:
        """Отобращает название в виде Пользователь/Рецепт."""
        return str(self.user) + '/' + str(self.recipe)


class Follow(models.Model):
    """Подписка на автора."""

    follower = models.ForeignKey(User,
                                 on_delete=models.CASCADE,
                                 related_name='follower')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='author')

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['follower', 'author'],
            name='unique_following'
        )]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        """Отобращает название в виде Подписчик/Автор."""
        return str(self.follower) + '/' + str(self.author)
