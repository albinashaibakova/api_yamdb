from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, permissions,
                            status, viewsets)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.views import APIView

from api.constants import INVALID_USERNAME, USER_PROFILE_PATH
from api.filters import TitleFilter
from api.mixins import ListCreateDestroyViewSet
from api.permissions import (IsAdminOrReadOnly,
                             IsAdminOrSuperuser,
                             IsAuthorAdminModeratorOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleListSerializer, TitleSerializer,
                             UserGetTokenSerializer, UserSerializer,
                             UserSignUpSerializer)
from api.utils import send_confirmation_email
from reviews.models import Category, Genre, Review, Title

User = get_user_model()


class UserSignUpView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.get(username=serializer.validated_data['username'])
        confirmation_code = default_token_generator.make_token(user)
        send_confirmation_email(email=user.email,
                                confirmation_code=confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserGetTokenView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = UserGetTokenSerializer(data=request.data)
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
            url_path=USER_PROFILE_PATH,
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
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitleListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    ordering = ('-year', 'name',)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleListSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthorAdminModeratorOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly
    )
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
    permission_classes = (
        IsAuthorAdminModeratorOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly
    )
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
