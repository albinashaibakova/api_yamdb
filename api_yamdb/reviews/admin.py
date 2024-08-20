from django.contrib import admin
from django.contrib.auth import get_user_model

from reviews.models import (Category, Comment, Genre,
                            Review, Title)


User = get_user_model()


@admin.register(User)
class YamdbUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'bio')
    search_fields = ('username', 'email')
    list_filter = ('role',)
    list_editable = ('role',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category', 'display_genre')
    search_fields = ('name', 'category__name')
    list_filter = ('category', 'year')
    list_editable = ('category',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'score', 'pub_date')
    search_fields = ('title',)
    list_filter = ('score', 'pub_date')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'review', 'pub_date')
    search_fields = ('author_review',)
    list_filter = ('pub_date',)
