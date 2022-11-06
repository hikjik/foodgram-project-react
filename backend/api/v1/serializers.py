from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework.serializers import (
    ModelSerializer,
    ReadOnlyField,
    SerializerMethodField,
)
from rest_framework.validators import UniqueValidator

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]

    def get_is_subscribed(self, obj):
        # TODO
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        ]
        extra_kwargs = {
            "email": {
                "required": True,
                "validators": [
                    UniqueValidator(
                        queryset=User.objects.all(),
                        message="Пользователь с таким email уже существует.",
                    ),
                ],
            },
            "first_name": {
                "required": True,
            },
            "last_name": {
                "required": True,
            },
        }


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "color", "slug"]


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class RecipeIngredientSerializer(ModelSerializer):
    id = ReadOnlyField(source="ingredient.id")
    name = ReadOnlyField(source="ingredient.name")
    measurement_unit = ReadOnlyField(source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = ["id", "name", "measurement_unit", "amount"]


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source="recipeingredient_set",
        many=True,
        read_only=True,
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        ]

    def get_is_favorited(self, obj):
        # TODO
        return False

    def get_is_in_shopping_cart(self, obj):
        # TODO
        return False
