from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet)

from api.permissions import IsAuthorOrReadOnly
from api.serializers import RecipeSerializer
from recipes.models import Ingredient, Recipe, Tag


class RecipeViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    # permission_classes = (IsAuthorOrReadOnly,)
    queryset = Recipe.objects.select_related('author')
    # queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# class FavouriteViewSet(ReadOnlyModelViewSet):
#     queryset = Favourite.objects.all()
#     serializer_class = FavouriteSerializer
#     permission_classes = (IsAuthenticatedOrReadOnly,)


# class FollowViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
#     serializer_class = FollowSerializer
#     permission_classes = (IsAuthenticated,)
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ('following__username',)

#     def get_queryset(self):
#         return self.request.user.follower.all()

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)
