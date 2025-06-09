from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('confirm/<int:order_id>/', views.order_confirm, name='order_confirm'),
    path('pay/<int:order_id>/', views.process_payment, name='process_payment'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('my-orders/', views.order_list, name='order_list'),
    path('my-orders/<int:order_id>/', views.order_details, name='order_details'),
    path('repeat/<int:order_id>/', views.repeat_order, name='repeat_order'),
]
