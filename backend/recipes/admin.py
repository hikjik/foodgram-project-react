from django.contrib import admin

from .models import Follow, Ingredient, Recipe, RecipeIngredient, Tag

admin.site.register([Follow, Ingredient, Recipe, RecipeIngredient, Tag])
