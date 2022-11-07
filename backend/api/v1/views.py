from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from recipes.models import Follow, Ingredient, Recipe, Tag
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet)

from .permissions import IsOwnerOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          TagSerializer, UserSubscribeSerializer)

User = get_user_model()


class TagsViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [AllowAny]


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ["^name"]


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = [IsOwnerOrReadOnly]


class SubscriptionViewSet(GenericViewSet):
    serializer_class = UserSubscribeSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    @action(methods=["GET"], detail=False)
    def subscriptions(self, request):
        authors = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(authors)
        serializer = self.get_serializer(pages, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=["POST", "DELETE"], detail=True)
    def subscribe(self, request, pk):
        user = self.request.user
        author = get_object_or_404(User, id=pk)
        subscription = user.follower.filter(author=author)

        if request.method == "POST":
            if user == author:
                data = {"errors": "Вы пытаетесь подписаться на самого себя."}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

            if subscription.exists():
                data = {"errors": ("Вы уже подписаны на этого автора")}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

            Follow.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if not subscription.exists():
                data = {"errors": "Вы не подписаны на указанного автора."}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
