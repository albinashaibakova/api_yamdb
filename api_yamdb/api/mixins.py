from django.contrib.auth import get_user_model
from rest_framework import (filters, mixins,
                            permissions,
                            viewsets)

from .permissions import IsAdminOrReadOnly

User = get_user_model()


class ListCreateDestroyViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)


class UserSignupTokenViewSet(mixins.CreateModelMixin,
                             viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
