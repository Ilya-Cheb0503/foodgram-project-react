from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

ModUser = get_user_model()


class Tag(models.Model):  # создаются лишь админом

    name = models.CharField(
        verbose_name='Название',
        max_length=100,
        unique=True
        )

    color = models.CharField(
        verbose_name='Цвет',
        max_length=7,
        unique=True
        )

    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
        max_length=100,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        verbose_name='Название',
        max_length=100
        )

    unit_of_measure = models.CharField(
        verbose_name='Единицы Измерения',
        max_length=50
        )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):

    author = models.ForeignKey(
        ModUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        )

    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты',
        )

    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='Тег',
        )

    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes_images/',
        null=True,
        blank=True,
        )

    name = models.CharField(
        verbose_name='Название',
        max_length=200
        )

    text = models.TextField(
        verbose_name='Описание'
        )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, мин',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'name'),
                name='unique_author_name'
            )
        ]

    def __str__(self):
        return self.name


class IngredientsRecipe(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Рецепт'
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_recipes',
        verbose_name='Ингредиент'
    )

    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredients_recipe'
            )
        ]
        db_table = 'recipes_ingredients_recipe'

    def __str__(self):
        return self.ingredient.name


class ShoppingList(models.Model):

    user = models.ForeignKey(
        ModUser,
        on_delete=models.CASCADE,
        related_name='list',
        verbose_name='Составитель списка покупок'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='list',
        verbose_name='Список покупок'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_list_user_recipes'
            )
        ]

    def __str__(self):
        return (f'Список покупок пользователя {self.user_id} содержит '
                f'следующие рецепты: {self.recipe_id}.')


class Favorite(models.Model):

    user = models.ForeignKey(
        ModUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Автор списка "Избранное"'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт в списке "Избранное"'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipes'
            )
        ]

    def __str__(self):
        return (f'Список "Избранное" пользователя {self.user_id} содержит '
                f'следующие рецепты: {self.recipe_id}.')
