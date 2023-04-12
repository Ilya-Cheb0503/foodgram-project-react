from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):

    name = models.CharField('Название', max_length=256)
    color = models.CharField('Цвет', max_length=16,)  # Исправить на цветовой
    # HEX-код (пример #49В64Е)
    slug = models.SlugField(
        'Слаг',
        unique=True,
        max_length=50,
    )


class Ingredient(models.Model):

    name = models.CharField('Название', max_length=50)
    amount = models.IntegerField('Количество')
    measure = models.CharField('Единицы Измерения', max_length=50)


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        )

    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        )

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        )

    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        blank=True,
        null=True,
        )

    name = models.CharField('Название', max_length=200)

    text = models.TextField('Описание', max_length=100)

    cooking_time = models.TimeField('Время приготовления')


class Follow(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )

    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "following"),
                name="unique_name_for_subscription")
        ]


class Favourite(models.Model):
    pass
