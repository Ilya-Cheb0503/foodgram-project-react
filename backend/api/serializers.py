from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserCreateSerializer, UserSerializer

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import Follow
from recipes.models import (Ingredient, IngredientsRecipe, Recipe, Tag)

UserModel = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )
        read_only_fields = (
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'unit_of_measure')


class UserCustomSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True
        )

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        fields = (
            'email', 'username', 'first_name',
            'last_name', 'password', 'id', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):

        user = self.context['request'].user

        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def validate(self, data):

        if 'password' in data:
            password = make_password(data['password'])
            data['password'] = password
            return data

        else:
            return data


class UserCustomCreateSerializer(UserCreateSerializer):

    class Meta:
        model = UserModel
        fields = UserCreateSerializer.Meta.fields + (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserLoginSerializer(serializers.Serializer):

    password = serializers.CharField(
        required=True,
        max_length=128
        )

    email = serializers.CharField(
        required=True,
        max_length=254
        )


class ChangePasswordSerializer(serializers.Serializer):

    new_password = serializers.CharField(
        required=True,
        max_length=128
        )

    current_password = serializers.CharField(
        required=True,
        max_length=128
        )


class FollowRecipeSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        )

    class Meta:
        model = Recipe
        fields = ('__all__')


class RecipeFollowSerializer(serializers.ModelSerializer):
    image = Base64ImageField()


class FollowSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(
        source='author.id'
        )

    email = serializers.ReadOnlyField(
        source='author.email'
        )

    username = serializers.ReadOnlyField(
        source='author.username'
        )

    first_name = serializers.ReadOnlyField(
        source='author.first_name'
        )

    last_name = serializers.ReadOnlyField(
        source='author.last_name'
        )

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    recipes_count = serializers.ReadOnlyField(
        source='author.recipes.count'
        )

    class Meta:
        model = Follow
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):

        return Follow.objects.filter(
            user=obj.user,
            author=obj.author
        ).exists()

    def get_recipes(self, obj):

        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = obj.author.recipes.all()
        if limit:
            queryset = queryset[:int(limit)]
        return FollowRecipeSerializer(queryset, many=True).data

    def validate(self, data):

        author_id = self.context.get('id')
        user_id = self.context.get('request').user.id

        if user_id == author_id:
            raise serializers.ValidationError(
                'На самого себя подписаться невозможно'
            )

        if Follow.objects.filter(
                user=user_id,
                author=author_id
        ).exists():
            raise serializers.ValidationError(
                'Нельзя подписаться дважды на одного пользователя'
            )
        return data


class RecipeGetSerializer(serializers.ModelSerializer):

    image = Base64ImageField(
        max_length=None,
        use_url=True
        )

    ingredients = serializers.SerializerMethodField()

    author = UserSerializer(
        read_only=True
        )

    tags = TagSerializer(
        many=True,
        read_only=True
        )

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'text', 'ingredients', 'tags',
                  'cooking_time', 'is_favorited', 'is_in_shopping_cart',
                  'image')
        read_only_fields = ('id', 'author', 'tags')

    def get_is_favorited(self, obj):

        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):

        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.cart.filter(user=user).exists()

    def get_ingredients(self, obj):

        recipe_ingredients = IngredientsRecipe.objects.filter(recipe=obj)
        return IngredientsRecipeGetSerializer(recipe_ingredients,
                                              many=True).data


class IngredientsRecipeGetSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(
        source='ingredient.id'
        )

    name = serializers.ReadOnlyField(
        source='ingredient.name'
        )

    unit_of_measure = serializers.ReadOnlyField(
        source='ingredient.unit_of_measure'
    )

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'name', 'unit_of_measure', 'amount')
        validators = (
            UniqueTogetherValidator(
                queryset=IngredientsRecipe.objects.all(),
                fields=('ingredient', 'recipe')
            )
        )


class IngredientsRecipeSerializer(serializers.ModelSerializer):

    recipe = serializers.PrimaryKeyRelatedField(
        read_only=True
        )

    amount = serializers.IntegerField(
        write_only=True
        )

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'amount', 'recipe')


class RecipeSerializer(serializers.ModelSerializer):

    ingredients = IngredientsRecipeSerializer(
        many=True
        )

    author = UserSerializer(
        read_only=True)

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )

    image = Base64ImageField(
        max_length=None,
        use_url=True)

    cooking_time = serializers.IntegerField(
        min_value=1
        )

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'text', 'ingredients', 'tags',
                  'cooking_time', 'image')
        read_only_fields = ('id', 'author', 'tags')

    def validate(self, data):

        ingredients = self.initial_data.get('ingredients')
        ingredients_list = [ingredient['id'] for ingredient in ingredients]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise serializers.ValidationError(
                ('Кажется, какой-то ингредиент повторяется. '
                 'Необходимо перепроверить список.')
            )
        return data

    def to_representation(self, instance):

        self.fields.pop('ingredients')
        self.fields.pop('tags')
        representation = super().to_representation(instance)
        representation['ingredients'] = IngredientsRecipeGetSerializer(
            IngredientsRecipe.objects.filter(recipe=instance), many=True
        ).data
        representation['tags'] = TagSerializer(
            instance.tags, many=True
        ).data
        return representation

    def create(self, validated_data):

        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        bulk_create_data = [
            IngredientsRecipe(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount'])
            for ingredient_data in ingredients_data
        ]
        IngredientsRecipe.objects.bulk_create(bulk_create_data)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in self.validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.set(tags_data)
        if 'ingredients' in self.validated_data:
            ingredients_data = validated_data.pop('ingredients')
            with transaction.atomic():
                amount_set = IngredientsRecipe.objects.filter(
                    recipe__id=instance.id)
                amount_set.delete()
                bulk_create_data = (
                    IngredientsRecipe(
                        recipe=instance,
                        ingredient=ingredient_data['ingredient'],
                        amount=ingredient_data['amount'])
                    for ingredient_data in ingredients_data
                )
                IngredientsRecipe.objects.bulk_create(bulk_create_data)
        return super().update(instance, validated_data)
