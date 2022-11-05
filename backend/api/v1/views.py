from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import Ingredient, Tag

from .serializers import IngredientSerializer, TagSerializer


class TagsViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ["^name"]
