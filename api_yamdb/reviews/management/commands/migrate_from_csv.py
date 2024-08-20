import csv
from typing import Any, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import models

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title

User = get_user_model()

ALLOWED_FILES_DICT: list[
    tuple[str, Any[models.Model], Optional[dict[str, str]]]
] = [
    ('category', Category, {}),
    ('genre', Genre, {}),
    ('titles', Title, {}),
    ('genre_title', GenreTitle, {}),
    ('users', User, {}),
    ('review', Review, {'title_id': 'title'}),
    ('comments', Comment, {'review_id': 'review'}),
]

COLUMN_FOREIGN_MODEL: dict[str, models.Model] = {
    'category': Category,
    'title_id': Title,
    'genre_id': Genre,
    'author': User,
    'review_id': Review,
}


def load_data(filename: str, model: models.Model, mappings: dict):
    with open(
            f'{settings.DATA_CSV_DIR}/{filename}.csv',
            encoding='utf-8'
    ) as file:
        reader = csv.DictReader(file)
        for row in reader:
            original = dict(row)
            data = dict(row)
            for key in original.keys():
                if key in COLUMN_FOREIGN_MODEL:
                    foreign_model: models.Model = COLUMN_FOREIGN_MODEL.get(key)
                    foreign_model_key = key
                    if key in mappings.keys():
                        data.pop(key)
                        foreign_model_key = mappings.get(key)
                    data[foreign_model_key] = foreign_model.objects.get(
                        pk=original[key]
                    )
            if not model.objects.filter(pk=data['id']).exists():
                model.objects.create(**data)


class Command(BaseCommand):
    help = 'import data from csv'

    def handle(self, *args, **options):
        for filename, model, mappings in ALLOWED_FILES_DICT:
            load_data(filename, model, mappings)
