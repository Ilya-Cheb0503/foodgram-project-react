from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
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
                             UserSerializer,
                             )
from api.filters import IngredientFilter, RecipeFilter
from api.paginators import PageLimitPagination
from recipes.models import (Favorite, Ingredient, IngredientsRecipe,
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
            message = 'Current Password is incorrect'
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

        author = get_object_or_404(
            UserModel,
            pk=self.kwargs.get('id')
        )

        follow = Follow.objects.filter(
            user=request.user,
            author=author
        )

        if follow.exists():
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
            message = 'This email has already been taken'
            return Response(
                data=message,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(UserModel, email=email)
        if not check_password(password, user.password):
            message = 'password is incorrect'
            return Response(
                data=message,
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)

        response = {
            'auth_token': str(token)
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

        is_favorited = self.request.query_params.get('is_favorited') or False

        if is_favorited:
            return Recipe.objects.filter(
                favorites__user=self.request.user
            )

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart') or False

        if is_in_shopping_cart:
            return Recipe.objects.filter(
                cart__user=self.request.user
            )

        return Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=('POST', 'DELETE'), )
    def favorite(self, request, pk):

        if self.request.method == 'POST':

            recipe = get_object_or_404(
                Recipe,
                pk=pk
            )

            favorite = Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            )

            if favorite.exists():
                return Response(
                    {'errors': 'Рецепт уже находится в списке "Избранное".'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Favorite.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )

            data = RecipeFollowSerializer(recipe).data
            return Response(
                data,
                status=status.HTTP_201_CREATED
            )

        recipe = get_object_or_404(Recipe, pk=pk)
        favorite = Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        )

        if favorite.exists():
            favorite.delete()
            return Response(
                'Рецепт успешно удален из списка "Избранное".',
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            {'errors': 'Данный рецепт отсутствует в списке "Избранное".'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=('POST', 'DELETE'), )
    def shopping_cart(self, request, pk):

        if request.method == 'POST':

            recipe = get_object_or_404(
                Recipe,
                pk=pk
            )

            shop_list = ShoppingList.objects.filter(
                user=request.user,
                recipe=recipe
            )

            if shop_list.exists():
                return Response(
                    {'errors': 'Рецепт уже находится в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            ShoppingList.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )

            data = RecipeFollowSerializer(recipe).data
            return Response(data, status=status.HTTP_201_CREATED)

        recipe = get_object_or_404(
            Recipe,
            pk=pk
        )

        follow = ShoppingList.objects.filter(
            user=request.user,
            recipe=recipe
        )

        if follow.exists():
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
    def download_shopping_cart(self, request):

        user = get_object_or_404(UserModel, username=request.user)
        recipes_id = ShoppingList.objects.filter(user=user).values('recipe')
        recipes = Recipe.objects.filter(pk__in=recipes_id)
        shop_list = {}
        n_rec = 0
        for recipe in recipes:
            n_rec += 1
            ing_amounts = IngredientsRecipe.objects.filter(recipe=recipe)
            for ing in ing_amounts:
                if ing.ingredient.name in shop_list:
                    shop_list[ing.ingredient.name][0] += ing.amount
                else:
                    shop_list[ing.ingredient.name] = [
                        ing.amount,
                        ing.ingredient.measurement_unit
                    ]

        text = ''
        for key, value in shop_list.items():
            text += f'\n{key} ({value[1]}) - {str(value[0])}'

        file = HttpResponse(
            f'Необходимые продукты:\n {text}', content_type='text/plain'
        )

        file['Content-Disposition'] = ('attachment; filename=cart.txt')
        return file


class FollowListViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        
        user = get_object_or_404(UserModel, username=self.request.user)
        return user.follower.all()
        # return Follow.objects.filter(user=self.request.user)
