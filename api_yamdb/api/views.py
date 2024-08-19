from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import (filters, permissions,
                            status, viewsets)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import INVALID_USERNAME
from reviews.models import Category, Genre, Review, Title
from .filters import TitleFilter
from .mixins import (ListCreateDestroyViewSet,
                     UserSignupTokenViewSet)
from .permissions import (IsAdminOrReadOnly,
                          IsAdminOrSuperuser,
                          IsAuthorAdminModeratorOrReadOnly)
from .serializers import (CategorySerializer,
                          GenreSerializer,
                          TitleSerializer,
                          TitleListSerializer,
                          UserGetTokenSerializer,
                          UserSerializer,
                          UserSignUpSerializer,
                          ReviewSerializer,
                          CommentSerializer
                          )
from .utils import send_confirmation_email

User = get_user_model()


class UserSignUpViewSet(UserSignupTokenViewSet):
    serializer_class = UserSignUpSerializer

    def create(self, request, *args, **kwargs):

        serializer = UserSignUpSerializer(data=request.data)
        if User.objects.filter(
                email=request.data.get('email'),
                username=request.data.get('username')).exists():
            user = get_object_or_404(User,
                                     email=request.data.get('email'))
            response_data = request.data
        else:
            serializer.is_valid(raise_exception=True)
            user = User.objects.create_user(**serializer.validated_data)
            response_data = serializer.data

        confirmation_code = default_token_generator.make_token(user)
        send_confirmation_email(email=user.email,
                                confirmation_code=confirmation_code)

        return Response(response_data, status=status.HTTP_200_OK)


class UserGetTokenViewSet(UserSignupTokenViewSet):
    serializer_class = UserGetTokenSerializer

    def create(self, request, *args, **kwargs):
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
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete',
                         'head', 'options')
    filter_backends = (filters.SearchFilter,)
    permission_classes = (IsAdminOrSuperuser,)

    @action(methods=('get', 'patch'),
            url_path=INVALID_USERNAME,
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def get_user_profile(self, request):
        if request.method == 'GET':
            user = get_object_or_404(User,
                                     username=request.user.username)
            serializer = UserSerializer(user)
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user,
                                    data=request.data,
                                    partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleListSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,)
    title_id_kwarg = 'title_id'
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs[self.title_id_kwarg])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,)
    review_id_kwarg = 'review_id'
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs[self.review_id_kwarg],
            title=get_object_or_404(Title, pk=self.kwargs['title_id']),
        )

    def get_queryset(self):
        return self.get_review().comments.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
