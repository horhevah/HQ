from django.contrib.auth.models import User
from django.db.models import Count, TextField
from django.db.models.functions import Cast
from django.http import JsonResponse, HttpRequest, HttpResponseNotFound, HttpResponse

from django.core.exceptions import BadRequest
from django.views.decorators.http import require_http_methods

from school.models import Product, Lesson


# Create your views here.


@require_http_methods(["GET"])
def lessons(request: HttpRequest) -> HttpResponse:
    """
    API viewe for lessons with filter by user and product
    :param request: HttpRequest with get data for filter (user_pk and product_pk)
    :return: JsonResponse with list of lessons
    """
    user_pk = request.GET.get('user_pk')
    product_pk = request.GET.get('product_pk')

    print('user_pk', user_pk)

    try:
        user = User.objects.get(pk=int(user_pk))
    except ValueError:
        raise BadRequest(f'Wrong user_pk format, need int, got {user_pk}')
    except User.DoesNotExist:
        return HttpResponseNotFound(f"Can't find user with pk= {user_pk}")

    available_products = [i.get('pk', 0) for i in user.used_products.all().values('pk')]
    try:
        product_pk_int = int(product_pk)
    except ValueError:
        raise BadRequest(f'Wrong product_pk format, need int, got {product_pk}')

    if product_pk_int in available_products:
        lessons_queryset = Lesson.objects.filter(product__pk=product_pk).values('lesson_name')
    else:
        return HttpResponseNotFound(f"Can't find available product with pk={product_pk} for user {user.username}")

    return JsonResponse(list(lessons_queryset), safe=False)


@require_http_methods(["GET"])
def products(request: HttpRequest) -> JsonResponse:
    """
    API view for get list of all products with number of lessons and students
    :param request: HttpRequest
    :return: JsonResponse with product data
    """
    print('aaaaaaaaaaaaaaaaaaaa')
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
    print(queryset)
    return JsonResponse(list(queryset), safe=False)
