from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe

User = get_user_model()


class IngredientFilter(FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="istartswith")


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name="tags__slug")

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            print(queryset)
            return queryset.filter(favorite=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(cart=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ["tags", "author"]
