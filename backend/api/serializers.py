from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Favourite, Follow, Recipe

User = get_user_model()


# class FavouriteSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Favourite
#         fields = '__all__'
#         ref_name = 'ReadOnlyFavourites'


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',)

    class Meta:
        model = Recipe
        fields = ('__all__')


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = '__all__'
        validators = (
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('following', 'user',),
                message="Невозможно подписаться на одного пользователя дважды"
            ),
        )

    def validate(self, data):
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(
                "Невозможно подписаться на одного пользователя дважды"
            )
        return data
