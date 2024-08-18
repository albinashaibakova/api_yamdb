import django_filters
from django_filters import FilterSet

from reviews.models import Title


class TitleFilter(FilterSet):
    year = django_filters.NumberFilter(field_name='year')
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='icontains')
    genre = django_filters.CharFilter(field_name='genre__slug',
                                      lookup_expr='iexact')
    category = django_filters.CharFilter(field_name='category__slug',
                                         lookup_expr='iexact')

    class Meta:
        model = Title
        fields = ('year', 'name', 'category', 'genre',)
