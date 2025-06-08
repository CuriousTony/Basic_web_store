from django.urls import path
from . import views

app_name = 'reviews'
urlpatterns = [
    path('', views.reviews, name='reviews'),
    path('order/<int:order_id>/bouquet/<int:bouquet_id>/review/', views.add_review, name='add_review'),
]
