from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class UserModel(AbstractUser):

    username = models.CharField(
        verbose_name='Никнейм',
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Никнейм содержит недопустимый(-е) символ(-ы)'
        )]
    )

    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        unique=True
    )

    first_name = models.CharField(
        verbose_name='Имя пользоветеля',
        max_length=150,
        blank=True
    )

    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        max_length=150,
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):

    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    author = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.user_id} подписан на {self.author_id}'
