from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import TagSerializer
from recipes.models import Tag


class TagsViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
