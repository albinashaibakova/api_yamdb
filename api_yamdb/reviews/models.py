from datetime import datetime

from django.core.validators import MaxValueValidator, RegexValidator
from django.db import models


NAME_FIELD_MAX_LENGTH = 256
SLUG_FIELD_MAX_LENGTH = 50


class Genre(models.Model):
    name = models.CharField(
        max_length=NAME_FIELD_MAX_LENGTH,
        verbose_name='Hазвание'
    )
    slug = models.SlugField(
        max_length=SLUG_FIELD_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(regex=r'^[-a-zA-Z0-9_]+$')
        ]
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'жанры'
        ordering = ('name',)


class Category(models.Model):
    name = models.CharField(
        max_length=NAME_FIELD_MAX_LENGTH,
        verbose_name='Hазвание'
    )
    slug = models.SlugField(
        max_length=SLUG_FIELD_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(regex=r'^[-a-zA-Z0-9_]+$')
        ]
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'категории'
        ordering = ('name',)


class Title(models.Model):
    name = models.CharField(
        max_length=NAME_FIELD_MAX_LENGTH,
        verbose_name='Hазвание',
    )
    description = models.TextField(
        null=True,
        verbose_name='Описание'
    )
    year = models.PositiveIntegerField(
        verbose_name='Год выпуска',
        validators=[
            MaxValueValidator(
                int(datetime.now().year),
                message='Год выпуска не может быть больше текущего.'
            )
        ],
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles',
        verbose_name='Жанр'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'произведения'
        ordering = ('-year', 'name')


class GenreTitle(models.Model):
    title_id = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    genre_id = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Жанр произведения'
        verbose_name_plural = 'жанры произведений'
        ordering = ('id', )
        constraints = [
            models.UniqueConstraint(
                fields=['title_id', 'genre_id'],
                name='genre_title_unique'
            )
        ]
