def bulk_create_data(model, instance, some_data):
    part_data = (
        model(
            recipe=instance,
            ingredient=ingredient_data['ingredient'],
            amount=ingredient_data['amount'])
        for ingredient_data in some_data
    )
    model.objects.bulk_create(part_data)

author=get_object_or_404(
                UserModel, pk=self.kwargs.get('id')
            )
if Follow.objects.filter(
    user=self.request.user,
    author=author
    ).exists():
    message = 'This email has already been taken'
    return Response(
        data=message,
        status=status.HTTP_400_BAD_REQUEST
        )


follow = Favorite.objects.filter(
    user=request.user,
    recipe=recipe
    )
if favorite.exist():
   favorite.delete() 


recipe = get_object_or_404(
    Recipe,
    pk=pk
)
favorite = Favorite.objects.filter(
            user=request.user,
            recipe=recipe
            )

if favorite.exist():
    return Response(
        {'errors': 'Рецепт уже находится в списке "Избранное".'},
        status=status.HTTP_400_BAD_REQUEST,
        )