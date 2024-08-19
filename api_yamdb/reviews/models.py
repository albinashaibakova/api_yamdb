from datetime import datetime

from django.core.validators import (MaxValueValidator,
                                    MinValueValidator,
                                    RegexValidator)
from django.contrib.auth.models import AbstractUser
from django.db import models
from api_yamdb.settings import (EMAIL_FIELD_MAX_LENGTH,
                                INVALID_CHAR,
                                NAME_FIELD_MAX_LENGTH,
                                ROLE_MAX_LENGTH,
                                SLUG_FIELD_MAX_LENGTH,
                                USERNAME_FIELD_MAX_LENGTH,
                                )
from api.validators import validator_for_username


class YamdbUser(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (ADMIN, ADMIN),
        (MODERATOR, MODERATOR),
        (USER, USER)
    )

    username = models.CharField(
        max_length=USERNAME_FIELD_MAX_LENGTH,
        unique=True,
        validators=(validator_for_username,)
    )
    email = models.EmailField(
        max_length=EMAIL_FIELD_MAX_LENGTH,
        unique=True,
        blank=False
    )
    bio = models.TextField(blank=True,
                           verbose_name='Bio')
    role = models.CharField(choices=ROLE_CHOICES,
                            default=USER,
                            max_length=ROLE_MAX_LENGTH,
                            verbose_name='Role')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN


class BaseGenreCategory(models.Model):
    name = models.CharField(
        max_length=NAME_FIELD_MAX_LENGTH,
        verbose_name='Hазвание'
    )
    slug = models.SlugField(
        max_length=SLUG_FIELD_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(regex=INVALID_CHAR)
        ]
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Genre(BaseGenreCategory):

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'жанры'
        ordering = ('name',)


class Category(BaseGenreCategory):

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'категории'
        ordering = ('name',)


class Title(models.Model):
    name = models.CharField(
        max_length=NAME_FIELD_MAX_LENGTH,
        verbose_name='Hазвание'
    )
    description = models.TextField(
        blank=True,
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
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=('title_id', 'genre_id'),
                name='genre_title_unique'
            )
        ]


class BaseCommentReview(models.Model):
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        abstract = True


class Review(BaseCommentReview):

    author = models.ForeignKey(
        YamdbUser,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=(
            MinValueValidator(
                1, message='Оценка должна быть 1 или больше.'
            ),
            MaxValueValidator(
                10, message='Оценка не может быть больше 10.'
            )
        )
    )

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_author_title'
            )
        ]
        ordering = ('-pub_date',)


class Comment(BaseCommentReview):

    author = models.ForeignKey(
        YamdbUser,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)
