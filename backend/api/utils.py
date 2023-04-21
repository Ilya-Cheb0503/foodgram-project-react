def bulk_create_data(model, instance, some_data):
    part_data = (
        model(
            recipe=instance,
            ingredient=ingredient_data['ingredient'],
            amount=ingredient_data['amount'])
        for ingredient_data in some_data
    )
    model.objects.bulk_create(part_data)
