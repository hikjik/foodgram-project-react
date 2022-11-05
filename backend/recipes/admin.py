from django.contrib import admin

from .models import Ingredient, Tag

admin.site.register([Tag, Ingredient])
