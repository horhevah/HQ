from school.models import Group


def shake_students():
    group = Group(
        group_name=f"{product.product_name}_1",
        product=product
    )
    group.save()
    group.students.add(User.objects.get(user_pk))