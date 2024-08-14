from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Category, CustomUser, Genre, GenreTitle, Title

UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('bio', 'role')}),
)

admin.site.register(Category)
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Genre)
admin.site.register(Title)
admin.site.register(GenreTitle)
