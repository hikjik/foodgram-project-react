from recipes.models import Ingredient, Recipe, Tag
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer


class TagsViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ["^name"]


class RecipeViewSet(ReadOnlyModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
