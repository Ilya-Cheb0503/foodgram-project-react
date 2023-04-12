from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views

from api.views import RecipeViewSet

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1_auth = routers.DefaultRouter()

# router_v1_auth.register('signup', SignUpViewSet, basename='signup')
# router_v1_auth.register('token', TokenViewSet, basename='token')
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet, basename='comments'
# )
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='viewsets'
# )

router_v1.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('v1/auth/', include(router_v1_auth.urls)),
    path('v1/', include(router_v1.urls)),
    path('v1/', include('djoser.urls.jwt')),
]
