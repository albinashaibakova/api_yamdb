from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import (filters, mixins, permissions,
                            status, viewsets)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Title
from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import (IsAdminOrReadOnly,
                          IsAdminOrSuperuser)
from .serializers import (CategorySerializer,
                          GenreSerializer,
                          TitleSerializer,
                          TitleListSerializer,
                          UserGetTokenSerializer,
                          UserSerializer,
                          UserSignUpSerializer)
from .utils import send_confirmation_email

User = get_user_model()


class UserSignUpViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):

        serializer = UserSignUpSerializer(data=request.data)
        if User.objects.filter(
                email=request.data.get('email'),
                username=request.data.get('username')).exists():
            user = get_object_or_404(User, email=request.data.get('email'))
            response_data = request.data
        else:
            serializer.is_valid(raise_exception=True)
            user = User.objects.create_user(**serializer.validated_data)
            response_data = serializer.data

        confirmation_code = default_token_generator.make_token(user)
        send_confirmation_email(email=user.email,
                                confirmation_code=confirmation_code)

        return Response(response_data, status=status.HTTP_200_OK)


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


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrSuperuser, )
    lookup_field = 'username'
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete',
                         'head', 'options')
    filter_backends = (filters.SearchFilter,)

    @action(methods=('get', 'patch'),
            url_path='me',
            permission_classes=(permissions.IsAuthenticated, ),
            detail=False)
    def get_user_profile(self, request):
        if request.method == 'GET':
            user = get_object_or_404(User, username=request.user.username)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UserSerializer(request.user,
                                        data=request.data,
                                        partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save(role=request.user.role)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
