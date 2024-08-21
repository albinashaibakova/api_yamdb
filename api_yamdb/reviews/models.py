from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)
from django.db import models

from api.validators import validator_for_username
from reviews.constants import (EMAIL_FIELD_MAX_LENGTH,
                               MAX_STR_VALUE_LENGTH, MAX_VALUE_SCORE,
                               MIN_VALUE_SCORE, NAME_FIELD_MAX_LENGTH,
                               ROLE_MAX_LENGTH, USERNAME_FIELD_MAX_LENGTH)
from reviews.validators import validate_year


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
        unique=True
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
        return self.username[:MAX_STR_VALUE_LENGTH]

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return (self.role == self.ADMIN
                or self.is_superuser)


class BaseGenreCategory(models.Model):
    name = models.CharField(
        max_length=NAME_FIELD_MAX_LENGTH,
        verbose_name='Hазвание'
    )
    slug = models.SlugField(unique=True)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:MAX_STR_VALUE_LENGTH]


class Genre(BaseGenreCategory):
    class Meta(BaseGenreCategory.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'жанры'


class Category(BaseGenreCategory):
    class Meta(BaseGenreCategory.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'категории'


class Title(models.Model):
    name = models.CharField(
        max_length=NAME_FIELD_MAX_LENGTH,
        verbose_name='Hазвание'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    year = models.SmallIntegerField(
        verbose_name='Год выпуска',
        validators=[validate_year],
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
        ordering = ('-year', 'name',)

    def __str__(self):
        return self.name[:MAX_STR_VALUE_LENGTH]


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
        ordering = ('title_id', 'genre_id')
        constraints = [
            models.UniqueConstraint(
                fields=('title_id', 'genre_id'),
                name='genre_title_unique'
            )
        ]

    def __str__(self):
        return f'Произведение {self.title_id} - Жанр {self.genre_id}'


class BaseCommentReview(models.Model):
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        YamdbUser,
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:MAX_STR_VALUE_LENGTH]


class Review(BaseCommentReview):

    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=(
            MinValueValidator(
                MIN_VALUE_SCORE,
                message=f'Оценка должна быть {MIN_VALUE_SCORE} или больше.'
            ),
            MaxValueValidator(
                MAX_VALUE_SCORE,
                message=f'Оценка не может быть больше {MAX_VALUE_SCORE}.'
            )
        )
    )

    class Meta(BaseCommentReview.Meta):
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_author_title'
            )
        ]


class Comment(BaseCommentReview):

    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE
    )

    class Meta(BaseCommentReview.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
