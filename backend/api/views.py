from io import StringIO
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404, get_list_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.serializers import (ChangePasswordSerializer, FollowSerializer,
                             IngredientSerializer, RecipeFollowSerializer,
                             RecipeGetSerializer, RecipeSerializer,
                             TagSerializer, UserLoginSerializer,
                             UserSerializer
                             )
from api.filters import IngredientFilter, RecipeFilter
from api.paginators import PageLimitPagination
from recipes.models import (Favorite, Ingredient,
                            Recipe, ShoppingList, Tag)
from users.models import Follow

UserModel = get_user_model()


class UserViewSet(viewsets.ModelViewSet):

    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny,)

    lookup_field = 'id'

    @action(
        detail=False,
        methods=('post',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def set_password(self, request, *args, **kwargs):

        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_user = self.request.user

        if not check_password(
                serializer.validated_data['current_password'],
                current_user.password
        ):
            message = "Current Password is incorrect"
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)

        current_user.set_password(serializer.validated_data['new_password'])
        current_user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):

        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):

        user = get_object_or_404(UserModel, pk=kwargs.get('id'))
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribeViewSet(viewsets.GenericViewSet,
                       mixins.CreateModelMixin,
                       mixins.DestroyModelMixin):

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FollowSerializer

    def perform_create(self, serializer):

        serializer.save(
            user=self.request.user,
            author=get_object_or_404(
                UserModel, pk=self.kwargs.get('id')
            )
        )

    def delete(self, request, *args, **kwargs):

        follow = get_object_or_404(
            Follow,
            user=self.request.user,
            author=get_object_or_404(
                UserModel, pk=self.kwargs.get('id')
            )
        )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_context(self):

        context = super().get_serializer_context()
        context['id'] = int(self.kwargs.get('id'))
        return context


class UserLoginViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,):

    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data, )
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data.get('password')
        email = serializer.validated_data.get('email')

        if UserModel.objects.filter(email=email).exists():
            message = "This email has already been taken"
            return Response(
                data=message,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(UserModel, email=email)
        if not check_password(password, user.password):
            message = "password is incorrect"
            return Response(
                data=message,
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)

        response = {
            "auth_token": str(token)
        }

        return Response(
            data=response,
            status=status.HTTP_201_CREATED
        )


class UserLogoutViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,):

    permission_classes = (IsAuthenticated,)
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):

        Token.objects.filter(user_id=self.request.user.id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
    permission_classes = (AllowAny,)


class RecipesViewSet(viewsets.ModelViewSet):

    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    queryset = Recipe.objects.all()

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response('Рецепт успешно удален',
                        status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):

        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipeSerializer

    def get_queryset(self):

        is_favorited = self.request.query_params.get('is_favorited') or 0
        if int(is_favorited) == 1:
            return Recipe.objects.filter(
                favorites__user=self.request.user
            )
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart') or 0
        if int(is_in_shopping_cart) == 1:
            return Recipe.objects.filter(
                cart__user=self.request.user
            )
        return Recipe.objects.all()

    def perform_create(self, serializer):

        serializer.save(author=self.request.user)

    @action(detail=True, methods=('POST', 'DELETE'), )
    def favorite(self, request, pk):

        if self.request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            if (Favorite.objects.filter(user=request.user,
               recipe=recipe).exists()):
                return Response(
                    {'errors': 'Рецепт уже находится в списке "Избранное".'},
                    status=status.HTTP_400_BAD_REQUEST,
                    )
            Favorite.objects.get_or_create(user=request.user, recipe=recipe)
            data = RecipeFollowSerializer(recipe).data
            return Response(data, status=status.HTTP_201_CREATED)
        recipe = get_object_or_404(Recipe, pk=pk)

        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            follow = get_object_or_404(Favorite, user=request.user,
                                       recipe=recipe)
            follow.delete()
            return Response(
                'Рецепт успешно удален из списка "Избранное".',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'errors': 'Данный рецепт отсутствует в списке "Избранное".'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=('POST', 'DELETE'), )
    def shopping_list(self, request, pk):

        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            if (ShoppingList.objects.filter(
               user=request.user, recipe=recipe).exists()):
                return Response(
                    {'errors': 'Рецепт уже находится в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            (ShoppingList.objects.get_or_create(
                user=request.user, recipe=recipe))
            data = RecipeFollowSerializer(recipe).data
            return Response(data, status=status.HTTP_201_CREATED)
        recipe = get_object_or_404(Recipe, pk=pk)

        if (ShoppingList.objects.filter(
           user=request.user, recipe=recipe).exists()):
            follow = get_object_or_404(ShoppingList, user=request.user,
                                       recipe=recipe)
            follow.delete()
            return Response(
                'Рецепт успешно удален из списка "Избранное".',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'errors': 'Данный рецепт отсутствует в списке "Избранное".'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=('GET',), )
    def download_shopping_list(request):

        user = request.user
        shop_list = get_list_or_404(
            ShoppingList.objects.select_related('recipe').prefetch_related(
                'recipe__ingredients_in_recipe'
            ),
            user=user
        )

        ingredients = []
        for i in shop_list:
            ingredients.extend(
                i.recipe.ingredients_in_recipe.all()
            )

        ingredients_dict = {}
        for i in ingredients:
            if i.ingredient_id not in ingredients_dict:
                ingredients_dict[i.ingredient_id] = 0
            ingredients_dict[i.ingredient_id] += i.amount

        data = StringIO()
        for i in ingredients_dict:
            ingredient = Ingredient.objects.get(id=i)
            text = f'{ingredient.name} ({ingredient.unit_of_measure}) —'
            text += f' {ingredients_dict[i]} \n'
            data.write(text)

        data.seek(0)
        headers = {
            'Content-Disposition': 'attachment; filename="list.txt"',
        }
        return Response(data, status=status.HTTP_200_OK, headers=headers)


class FollowListViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)
