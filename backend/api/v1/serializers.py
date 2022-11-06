from django.contrib.auth import get_user_model
from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.validators import UniqueValidator, ValidationError

from .fields import Base64ImageField

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


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

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

    def get_ingredients(self, recipe):
        return recipe.ingredients.values(
            "id",
            "name",
            "measurement_unit",
            amount=F("recipes_ingredients__amount"),
        )

    def get_is_favorited(self, recipe):
        # TODO
        return False

    def get_is_in_shopping_cart(self, recipe):
        # TODO
        return False

    def validate_name(self, name):
        author = self.context["request"].user
        if self.context["request"].method == "POST":
            if Recipe.objects.filter(author=author, name=name).exists():
                message = f"Рецепт с названием {name} уже существует."
                raise ValidationError({"name": message})
        return name

    def validate_tags(self, tags):
        if tags is None:
            raise ValidationError({"tags": "Обязательное поле."})

        for id in tags:
            if not Tag.objects.filter(id=id).exists():
                message = f"Тег с id={id} не найден."
                raise ValidationError({"tags": message})

        return tags

    def validate_ingredients(self, ingredients):
        if ingredients is None:
            raise ValidationError({"ingredients": "Обязательное поле."})

        if not ingredients:
            message = "Пустой список ингредиентов."
            raise ValidationError({"ingredients": message})

        if len(ingredients) != len({i["id"] for i in ingredients}):
            message = "Список ингредиентов не должен содержать повторы"
            raise ValidationError({"ingredients": message})

        for ingredient in ingredients:
            if not isinstance(ingredient, dict):
                message = (
                    f"Недопустимые данные. "
                    f"Ожидался dict, но был получен {type(ingredient)}."
                )
                ValidationError({"ingredients": message})
            if "id" not in ingredient or "amount" not in ingredient:
                message = "Отсутствуют обязательные поля."
                raise ValidationError({"ingredients": message})

            id = ingredient["id"]
            if not Ingredient.objects.filter(id=id).exists():
                message = f"Ингредиент с id={id} не найден."
                raise ValidationError({"ingredients": message})

        return ingredients

    def validate(self, data):
        data["tags"] = self.validate_tags(self.initial_data.get("tags"))
        data["ingredients"] = self.validate_ingredients(
            self.initial_data.get("ingredients")
        )
        data["author"] = self.context["request"].user
        return data

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(**validated_data)

        self._set_tags(recipe, tags)
        self._set_ingredients(recipe, ingredients)

        return recipe

    def update(self, recipe, validated_data):
        recipe.image = validated_data.get("image", recipe.image)
        recipe.name = validated_data.get("name", recipe.name)
        recipe.text = validated_data.get("text", recipe.text)
        recipe.cooking_time = validated_data.get(
            "cooking_time", recipe.cooking_time
        )
        self._set_tags(recipe, validated_data.get("tags"))
        self._set_ingredients(recipe, validated_data.get("ingredients"))
        recipe.save()
        return recipe

    @staticmethod
    def _set_tags(recipe, tags):
        recipe.tags.clear()
        recipe.tags.set(tags)

    @staticmethod
    def _set_ingredients(recipe, ingredients):
        recipe.ingredients.clear()
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient["id"],
                amount=ingredient["amount"],
            )
