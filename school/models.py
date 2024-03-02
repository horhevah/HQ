import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count

from django.db.models.signals import m2m_changed
from django.dispatch import receiver


class Product(models.Model):
    product_name = models.CharField(null=True, max_length=255, verbose_name='product_name')
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='written_products')
    start_datetime = models.DateTimeField(auto_now_add=False,  verbose_name='start_datetime')
    price = models.IntegerField(null=False, verbose_name='price')
    students = models.ManyToManyField(User, related_name='used_products')
    max_users_in_group = models.IntegerField(null=False, verbose_name='max_users_in_group')
    min_users_in_group = models.IntegerField(null=False, verbose_name='min_users_in_group')

    def __str__(self):
        return self.product_name


class Lesson(models.Model):
    lesson_name = models.CharField(null=True, max_length=255, verbose_name='lesson_name')
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, related_name='lessons')
    video_url = models.URLField(verbose_name='video_url')

    def __str__(self):
        return self.lesson_name


class Group(models.Model):
    group_name = models.CharField(null=True, max_length=255, verbose_name='group_name')
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, related_name='group')
    students = models.ManyToManyField(User, related_name='school_groups')

    def __str__(self):
        return self.group_name




# default behavior signal handler

"""
Я знаю, что решение неверно  как минимум потому что не учитывает минимальное кол-во студентов в группе,
но решил сдать это, т.к. это уже лучше, чем отсутсвие решения.

Задание было для меня неожиданностью, поэтому было сложно выделить на него время
"""

def fill_group_default(sender, **kwargs):
    print('action', kwargs["action"])
    if kwargs["action"] == "post_add":
        now_datetime = datetime.datetime.now()
        start_product_datetime = kwargs["instance"].start_datetime
        user_list = list(kwargs["pk_set"])
        if not kwargs["instance"].group.count():
            fill_empty_product(kwargs["instance"], user_list)
        elif now_datetime < start_product_datetime:
            fill_product_before_start(kwargs["instance"], user_list)
        else:
            fill_product_after_start(kwargs["instance"], user_list)


def fill_empty_product(product: Product, user_list: list) -> None:
    new_group_count = (len(user_list) // product.max_users_in_group) + 1
    new_groups = []
    for group in range(new_group_count):
        new_group = Group(
            group_name=f"{product.product_name}_{group + 1}",
            product=product
        )
        new_group.save()
        new_groups.append(new_group)
    for n, user_pk in enumerate(user_list):
        user_to_add = User.objects.get(pk=user_pk)
        new_groups[n % new_group_count].students.add(user_to_add)


def fill_product_before_start(product: Product, user_list: list) -> None:
    # check if groups already exist
    free_spots_number = product.group.count() - product.students.count()
    if len(user_list) < free_spots_number:
        for user_pk in user_list:
            group_with_min_load = product.group.all().annotate(students_count=Count('students')).order_by(
                'students_count').first()
            user = User.objects.get(user_pk)
            group_with_min_load.students.add(user)
    else:
        new_group_count = len(user_list) // product.max_users_in_group + 1
        group_count = product.group.count()
        for group in range(new_group_count):
            new_group = Group(
                group_name=f"{product.product_name}_{group_count + group + 1}",
                product=product
            )
            new_group.save()
        groups = product.group.all().order_by('group_name')
        for group in groups:
            group.students.clear()
        groups_count = product.group.count()
        for n, user_pk in enumerate(list(product.students.all()) + user_list):
            user_to_add = User.objects.get(pk=user_pk)
            list(groups)[n % groups_count].students.add(user_to_add)


def fill_product_after_start(product: Product, user_list: list) -> None:
    free_spots_number = product.group.count() - product.students.count()
    if len(user_list) < free_spots_number:
        for user_pk in user_list:
            group_with_min_load = product.group.all().annotate(students_count=Count('students')).order_by(
                'students_count').first()
            user = User.objects.get(user_pk)
            group_with_min_load.students.add(user)
    else:
        new_group_count = (len(user_list) // product.max_users_in_group) + 1
        new_groups = []
        for group in range(new_group_count):
            new_group = Group(
                group_name=f"{product.product_name}_{group + 1}",
                product=product
            )
            new_group.save()
            new_groups.append(new_groups)
        for n, user_pk in enumerate(user_list):
            user_to_add = User.objects.get(pk=user_pk)
            new_groups[n % new_group_count].students.add(user_to_add)



m2m_changed.connect(fill_group_default,sender=Product.students.through)