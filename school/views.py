from django.db.models import Count, TextField
from django.db.models.functions import Cast
from django.http import JsonResponse, HttpRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from school.models import Product


# Create your views here.


@require_http_methods(["GET"])
def lessons(request: HttpRequest) -> JsonResponse:
    """
    API viewe for lessons with filter by user and product
    :param request: HttpRequest with get data for filter (user_pk and product_pk)
    :return: JsonResponse with list of lessons
    """
    user_pk = request.GET.get('user_pk')
    product_pk = request.GET.get('product_pk')



@require_http_methods(["GET"])
def products(request: HttpRequest) -> JsonResponse:
    """
    API view for get list of all products with number of lessons and students
    :param request: HttpRequest
    :return: JsonResponse with product data
    """
    queryset = Product.objects.all().values(
        'product_name',
        'author__username',
        'number_of_lessons',
        'price',
        'students',
        'max_users_in_group',
        'min_users_in_group',
        start_datetime_str=Cast('start_datetime', TextField()),
        number_of_lessons=Count('lessons'),
        number_of_students=Count('students')

    )

    return JsonResponse(queryset)
