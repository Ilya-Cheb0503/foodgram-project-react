from django.contrib import admin

from recipes.models import (Tag, Ingredient, Recipe,
                            IngredientsRecipe, ShoppingList,
                            Favorite,
                            )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'measurement_unit',
    )

    search_fields = (
        'name',
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'color',
        'slug'
    )

    search_fields = (
        'name',
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    list_display = (
        'author',
        'name',
        'image',
        'view_text',
        'cooking_time',
        'count_favorite',
    )

    search_fields = (
        'name',
        'author',
        'tags'
    )

    readonly_fields = ('count_favorite',)

    def view_text(self, obj):
        return obj.text[:100]

    def count_favorite(self, obj):
        return obj.favorites.select_related('user').count()


@admin.register(IngredientsRecipe)
class IngredientsRecipeAdmin(admin.ModelAdmin):

    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )

    search_fields = (
        'ingredient',
    )


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'recipe',
    )

    search_fields = (
        'user',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'recipe',
    )

    search_fields = (
        'user',
    )
