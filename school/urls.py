from django.urls import path
from . import views


app_name = 'school'

urlpatterns = [
    path('products', views.products, name='products'),
    path('lessons', views.lessons, name='lessons')
]