import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    genre = django_filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='iexact'
    )
    category = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='iexact'
    )

    class Meta:
        model = Title
        fields = ('year', 'name', 'category', 'genre',)
