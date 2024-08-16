from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import (filters, mixins, permissions,
                            status, viewsets, pagination)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Title, Review, Comment
from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import IsAdminOrReadOnly
from .serializers import (CategorySerializer,
                          GenreSerializer,
                          TitleSerializer,
                          TitleListSerializer,
                          UserGetTokenSerializer,
                          UserSignUpSerializer,
                          ReviewSerializer,
                          CommentSerializer)
from .utils import send_confirmation_email

User = get_user_model()


class UserSignUpViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        User.objects.create(**serializer.validated_data)
        user = User.objects.get(username=serializer.validated_data['username'])
        confirmation_code = default_token_generator.make_token(user)
        send_confirmation_email(email=user.email,
                                confirmation_code=confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserGetTokenViewSet(mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserGetTokenSerializer
    permission_classes = (permissions.AllowAny, )

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if default_token_generator.check_token(user, confirmation_code):
            token = AccessToken.for_user(user)
            message = {'token': str(token)}
            return Response(message, status=status.HTTP_200_OK)
        else:
            bad_request_message = {'Error': 'Отсутствует'
                                            ' обязательное поле или оно некорректно'}
            return Response(bad_request_message, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleListSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):

    serializer_class = ReviewSerializer
    agination_class = pagination.PageNumberPagination
    title_id_kwarg = 'title_id'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs[self.title_id_kwarg])

    def get_queryset(self):
        return self.get_title().reviews.all()

    @property
    def allowed_methods(self):
        methods = super().allowed_methods
        return [method for method in methods if method != 'PUT']

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentsViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer
    review_id_kwarg = 'review_id'
    pagination_class = pagination.PageNumberPagination

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs[self.review_id_kwarg]
        )

    def get_queryset(self):
        return self.get_review().comments.select_related('author')

    @property
    def allowed_methods(self):
        methods = super().allowed_methods
        return [method for method in methods if method != 'PUT']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
