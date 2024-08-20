from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (CategoryViewSet, CommentsViewSet, GenreViewSet,
                       ReviewViewSet, TitleViewSet, UserGetTokenViewSet,
                       UserSignUpViewSet, UsersViewSet)


v1_router = SimpleRouter()
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('users', UsersViewSet, basename='user')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comments'
)


auth_urls = [
    path('signup/', UserSignUpView.as_view(),
         name='signup'),
    path('token/', UserGetTokenView.as_view(),
         name='token')
]

urlpatterns = [
    path(
        'v1/', include([
            path('auth/', include(auth_urls)),
            path('', include(v1_router.urls)),
        ])
    )
]
