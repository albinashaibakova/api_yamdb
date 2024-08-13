from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import CategoryViewSet


v1_router = SimpleRouter()
v1_router.register('categories', CategoryViewSet, basename='categories')


urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
