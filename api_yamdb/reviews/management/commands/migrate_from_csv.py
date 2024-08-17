import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from api_yamdb.settings import DATA_CSV_DIR
from reviews.models import *

User = get_user_model()

ALLOWED_FILES_DICT = (
    ('category', Category),
    ('genre', Genre),
    ('titles', Title),
    ('genre_title', GenreTitle),
    ('users', User),
    #todo
    # ('review', Review),
    # ('comments', Comment),
)

COLUMN_FOREIGN_MODEL = {
    'category': Category,
    'title_id': Title,
    'genre_id': Genre,
    'author': User,
    # 'review_id': Review,
}


def load_data(filename: str, model: models.Model):
    with open(f'{DATA_CSV_DIR}/{filename}.csv', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data = dict(row)
            for key in data.keys() :
                if key in COLUMN_FOREIGN_MODEL:
                    foreign_model = COLUMN_FOREIGN_MODEL.get(key)
                    data[key] = foreign_model.objects.get(pk=data[key])
            model.objects.update_or_create(**data)


class Command(BaseCommand):
    help = 'import data from csv'

    def handle(self, *args, **options):
        for filename, model in ALLOWED_FILES_DICT:
            load_data(filename, model)
