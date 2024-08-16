from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (CategoryViewSet,
                    GenreViewSet,
                    TitleViewSet,
                    UserGetTokenViewSet,
                    UserSignUpViewSet,
                    CommentsViewSet,
                    ReviewViewSet
                    )


v1_router = SimpleRouter()
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comments'
)


auth_urls = [
    path('signup/', UserSignUpViewSet.as_view({'post': 'create'}),
         name='signup'),
    path(
        'token/', UserGetTokenViewSet.as_view({'post': 'create'}), name='token')
]

urlpatterns = [
    path('v1/auth/', include(auth_urls)),
    path('v1/', include(v1_router.urls))

]
