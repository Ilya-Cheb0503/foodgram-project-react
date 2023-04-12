from django.contrib import admin

from recipes.models import Ingredient, Recipe, Tag

SYMBOLS_LIMIT = 150


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    list_display = ('pk', 'name', 'text', 'cooking_time',)
    search_fields = ('name',)
    list_editable = ('text',)
    list_display_links = ('name',)
    empty_value_display = '-пусто-'

    def __str__(self):
        return self.name[:SYMBOLS_LIMIT]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'amount', 'measure',)
    list_display_links = ('name',)
    list_editable = ('amount', 'measure',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'color',)
    prepopulated_fields = {"slug": ("name",)}
    list_display_links = ('name',)
    list_editable = ('color',)