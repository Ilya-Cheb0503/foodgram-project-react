import django_filters
from django.contrib.auth import get_user_model
from recipes.models import Ingredient, Recipe, Tag

ModUser = get_user_model()


class IngredientFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name', 'unit_of_measure')


class RecipeFilter(django_filters.FilterSet):

    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        )

    author = django_filters.ModelChoiceFilter(
        queryset=ModUser.objects.all()
        )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
