from django.urls import path
from . import views

app_name = 'cart'
urlpatterns = [
    path('add/<int:bouquet_id>/', views.add_to_cart, name='add_to_cart'),
    path('', views.cart_detail, name='cart_detail'),
    path('update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
]
