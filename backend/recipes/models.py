import re

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=32,
        unique=True,
        verbose_name="Название тега",
    )
    slug = models.SlugField(
        max_length=32,
        unique=True,
        verbose_name="Slug тега",
    )
    color = models.CharField(
        max_length=7,
        validators=[
            RegexValidator(
                re.compile("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"),
                "Введите корректный цветовой hex-код (например, #49B64E)",
            ),
        ],
        verbose_name="Цвет тега",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name="Название ингридиента",
    )
    measurement_unit = models.CharField(
        max_length=16,
        verbose_name="Единицы измерения",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique ingredient",
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги рецепта",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        verbose_name="Ингредиенты рецепта",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта",
    )
    image = models.ImageField(
        upload_to="recipes/images",
        verbose_name="Изображение рецепта",
    )
    text = models.TextField(
        verbose_name="Описание рецепта",
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=1,
                message="Время приготовления должно быть больше 1 минуты",
            )
        ],
        verbose_name="Время приготовления в минутах",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации рецепта",
    )
    favorite = models.ManyToManyField(
        User,
        related_name="favorites",
        verbose_name="В избранном у пользователей",
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="recipes_ingredients",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингридиент",
        related_name="recipes_ingredients",
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=1,
                message="Количество должно быть больше 1",
            ),
        ],
        verbose_name="Количество",
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Рецепт и ингридиент"
        verbose_name_plural = "Рецепты и ингридиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique recipe ingredient",
            )
        ]

    def __str__(self):
        return (
            f"Рецепт {self.recipe}, "
            f"Ингредиент: {self.ingredient}, "
            f"Количество: {self.amount}"
        )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )

    def __str__(self):
        return f"Подписчик: {self.user}, Автор: {self.author}"

    class Meta:
        ordering = ["-id"]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique follow",
            )
        ]
