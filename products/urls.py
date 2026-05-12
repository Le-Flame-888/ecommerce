from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('search-autocomplete/', views.search_autocomplete, name='search_autocomplete'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
