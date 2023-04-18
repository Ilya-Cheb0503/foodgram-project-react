from django.urls import include, path
from rest_framework import routers

from api.views import (FollowListViewSet, IngredientsViewSet, RecipesViewSet,
                       SubscribeViewSet, TagsViewSet, UserLoginViewSet,
                       UserLogoutViewSet, UserViewSet)

app_name = 'api'

router_auth = routers.DefaultRouter()
router = routers.DefaultRouter()

router_auth.register(
    'token/login/',
    UserLoginViewSet,
    basename='login'
    )

router_auth.register(
    'token/logout',
    UserLogoutViewSet,
    basename='logout'
    )

router.register(
    'tags',
    TagsViewSet,
    basename='tags'
    )

router.register(
    'ingredients',
    IngredientsViewSet,
    basename='ingredients'
    )

router.register(
    'recipes',
    RecipesViewSet,
    basename='recipes'
    )

router.register(
    'users/subscriptions',
    FollowListViewSet,
    basename='subscriptions_list'
)

router.register(
    r'users/(?P<id>\d+)/subscribe',
    SubscribeViewSet,
    basename='subscribe'
)

router.register(
    'users',
    UserViewSet,
    basename='users'
    )

urlpatterns = [
    path('auth/', include(router_auth.urls)),
    path('', include(router.urls)),
]
