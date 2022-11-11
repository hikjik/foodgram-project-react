"""Модуль содержит основные модели проекта."""
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель Tag для рецептов.

    Описывает метки, с помощью которых пользователи размечают публикации,
    что упрощает поиск подходящих рецептов.
    """

    class Color(models.TextChoices):
        """Enum-класс Color перечисляет цвета тегов в hex-кодировке."""

        RED = "#FF0000", "Красный"
        ORANGE = "#FF9933", "Оранжевый"
        YELLOW = "#FFFF00", "Желтый"
        GREEN = "#00FF00", "Зеленый"
        BLUE = "#0000FF", "Синий"
        PURPLE = "#6600CC", "Фиолетовый"
        WHITE = "#FFFFFF", "Белый"
        BLACK = "#000000", "Черный"

    name = models.CharField(
        max_length=32,
        unique=True,
        verbose_name="Название",
    )
    slug = models.SlugField(
        max_length=32,
        unique=True,
        verbose_name="Slug",
    )
    color = models.CharField(
        max_length=10,
        choices=Color.choices,
        default=Color.RED,
        verbose_name="Цвет",
    )

    class Meta:
        """Meta опции модели Tag."""

        ordering = ("id",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        """Строковое представление модели Tag."""
        return self.name


class Ingredient(models.Model):
    """Модель Ingredient.

    Описывает продукты, необходимые для приготовления блюда по рецепту
    """

    name = models.CharField(
        max_length=128,
        verbose_name="Название",
    )
    measurement_unit = models.CharField(
        max_length=16,
        verbose_name="Единицы измерения",
    )

    class Meta:
        """Meta опции модели Ingredient."""

        ordering = ("id",)
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique ingredient",
            )
        ]

    def __str__(self):
        """Строковое представление модели Ingredient."""
        return self.name


class Recipe(models.Model):
    """Модель Recipe.

    Описывает рецепты, которые пользователи публикуют на сервисе.
    """

    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        verbose_name="Ингредиенты",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название",
    )
    image = models.ImageField(
        upload_to="recipes/images",
        verbose_name="Изображение",
    )
    text = models.TextField(
        verbose_name="Описание",
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
        verbose_name="Дата публикации",
    )
    favorite = models.ManyToManyField(
        User,
        related_name="favorites",
        verbose_name="В избранном у пользователей",
    )
    cart = models.ManyToManyField(
        User,
        related_name="carts",
        verbose_name="В корзине у пользователей",
    )

    class Meta:
        """Meta опции модели RecipeIngredient."""

        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        """Строковое представление модели Recipe."""
        return self.name


class RecipeIngredient(models.Model):
    """Модель RecipeIngredient.

    Вспомогательная модель, связующая модели Recipe и Ingredient.
    Хранит дополнительное поле amount - количество ингредиента в рецепте.
    """

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
        """Meta опции модели Recipe."""

        ordering = ("-id",)
        verbose_name = "Рецепт и ингридиент"
        verbose_name_plural = "Рецепты и ингридиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique recipe ingredient",
            )
        ]

    def __str__(self):
        """Строковое представление модели RecipeIngredient."""
        return (
            f"Рецепт {self.recipe}, "
            f"Ингредиент: {self.ingredient}, "
            f"Количество: {self.amount}"
        )


class Follow(models.Model):
    """Модель Follow.

    Позволяет создавать подписки на публикации пользователей.
    """

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
        """Строковое представление модели Follow."""
        return f"Подписчик: {self.user}, Автор: {self.author}"

    class Meta:
        """Meta опции модели Follow."""

        ordering = ("-id",)
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique follow",
            )
        ]
