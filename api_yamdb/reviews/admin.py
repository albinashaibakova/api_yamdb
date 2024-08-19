from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, YamdbUser)

UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('bio', 'role')}),
)

admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(YamdbUser, UserAdmin)
admin.site.register(Genre)
admin.site.register(Review)
admin.site.register(Title)
admin.site.register(GenreTitle)
