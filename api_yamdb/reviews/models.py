from datetime import datetime

from django.core.validators import MaxValueValidator, RegexValidator
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


NAME_FIELD_MAX_LENGTH = 256
SLUG_FIELD_MAX_LENGTH = 50
USERNAME_FIELD_MAX_LENGTH = 150
EMAIL_FIELD_MAX_LENGTH = 254
FIRST_NAME_FIELD_MAX_LENGTH = 150
LAST_NAME_FIELD_MAX_LENGTH = 150
ROLE_MAX_LENGTH = 20

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

ROLE_CHOICES = (
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
    (USER, USER)
)


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=USERNAME_FIELD_MAX_LENGTH,
        unique=True,
        blank=False,
        validators=[
            RegexValidator(regex=r'^[\w.@+-]+\Z')
        ]
    )
    email = models.EmailField(
        max_length=EMAIL_FIELD_MAX_LENGTH,
        unique=True,
        blank=False
    )
    first_name = models.CharField(
        max_length=NAME_FIELD_MAX_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        max_length=LAST_NAME_FIELD_MAX_LENGTH,
        blank=True
    )
    bio = models.TextField(blank=True,
                           verbose_name="Bio")
    role = models.CharField(choices=ROLE_CHOICES,
                            default='user',
                            max_length=ROLE_MAX_LENGTH,
                            verbose_name="Role")

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_user(self):
        return self.role == USER


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
