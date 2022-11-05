import re

from django.core.validators import RegexValidator
from django.db import models


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
