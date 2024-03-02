import datetime

from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from school import services


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
@receiver(m2m_changed, sender=Product)
def fill_group_default(sender, product, action, reverse, model, user_set, **kwargs):
    if action == "post_add":
        now_datetime = datetime.datetime.now()
        start_product_datetime = product.start_datetime
        if now_datetime < start_product_datetime:
            user_list = list(user_set)
            # check if groups already exist
            if product.groups.count() != 0:
                for user_pk in user_list:
                    group_with_min_load = sorted(product.groups, key=lambda x: len(x.studets.count()))[0]
                    if group_with_min_load.students.count() < product.max_users_in_group:
                        user = User.objects.get(user_pk)
                        group_with_min_load.students.add(user)
                    else:
                        services.shake_students()
                        # group = Group(
                        #     group_name=f"{product.product_name}_{product.groups.count() + 1}",
                        #     product=product
                        # )
                        # group.save()
                        # group.students.add(User.objects.get(user_pk))

            else:
                services.shake_students()



