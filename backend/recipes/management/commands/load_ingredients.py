import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--path", type=str)

    def handle(self, *args, **options):
        with open(options["path"], "r", encoding="utf-8") as json_file:
            for ingredient in json.load(json_file):
                Ingredient.objects.create(**ingredient)
