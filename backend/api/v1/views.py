"""Модуль содержит обработчики запросов к API."""
import csv

from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Follow, Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet)

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsOwnerOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer, TagSerializer,
                          UserSubscribeSerializer)

User = get_user_model()


class TagsViewSet(ReadOnlyModelViewSet):
    """Вьюсет, позволяющий получить данные модели Tag."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет, позволяющий получить данные модели Ingredient."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Вьюсет для работы с рецептами.

    Позволяет получать/создавать/редактировать/удалять рецепты,
    добавлять рецепты в избранное и в корзину, скачивать список покупок.
    """

    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(
        methods=("POST", "DELETE"),
        detail=True,
        serializer_class=ShortRecipeSerializer,
    )
    def favorite(self, request, pk):
        """Метод добавляет/удаляет рецепт в избранное."""
        recipe = get_object_or_404(Recipe, id=pk)
        manager = request.user.favorites

        if self.request.method == "POST":
            return self._add_recipe(manager, recipe)

        if self.request.method == "DELETE":
            return self._remove_recipe(manager, recipe)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        methods=("POST", "DELETE"),
        detail=True,
        serializer_class=ShortRecipeSerializer,
    )
    def shopping_cart(self, request, pk):
        """Метод добавляет/удаляет рецепт в корзину."""
        recipe = get_object_or_404(Recipe, id=pk)
        manager = request.user.carts

        if self.request.method == "POST":
            return self._add_recipe(manager, recipe)

        if self.request.method == "DELETE":
            return self._remove_recipe(manager, recipe)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=("GET",), detail=False)
    def download_shopping_cart(self, request):
        """Возвращает список покупок в формате csv.

        В списке должны быть перечислены ингредиенты,
        необходимые для приготовления блюд, добавленных в корзину пользователя.
        """
        user = request.user
        if not user.carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__in=user.carts.all(),
            )
            .values(
                name=F("ingredient__name"),
                unit=F("ingredient__measurement_unit"),
            )
            .annotate(total_amount=Sum("amount"))
        )

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment;filename=cart.csv"

        writer = csv.writer(response)
        writer.writerow(ingredients.first().keys())
        for ingredient in list(ingredients):
            writer.writerow(ingredient.values())
        return response

    def _add_recipe(self, manager, recipe):
        if manager.filter(id=recipe.id).exists():
            data = {"errors": "Рецепт был добавлен ранее."}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        manager.add(recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _remove_recipe(self, manager, recipe):
        if not manager.filter(id=recipe.id).exists():
            data = {"errors": "Рецепт не найден."}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        manager.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(GenericViewSet):
    """Вьюсет для управления подписками пользователей."""

    serializer_class = UserSubscribeSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    @action(methods=("GET",), detail=False)
    def subscriptions(self, request):
        """Метод для получения списка подписок."""
        authors = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(authors)
        serializer = self.get_serializer(pages, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=("POST", "DELETE"), detail=True)
    def subscribe(self, request, pk):
        """Метод создаёт/удаляет подписки на публикации пользователей."""
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

        if request.method == "DELETE":
            if not subscription.exists():
                data = {"errors": "Вы не подписаны на указанного автора."}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
