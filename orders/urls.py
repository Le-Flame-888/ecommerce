from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('cancel/<int:order_id>/', views.order_cancel, name='order_cancel'),
]
