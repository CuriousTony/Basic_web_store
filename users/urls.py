from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView
from . import views

app_name = 'users'
urlpatterns = [
    path('signin/', CustomLoginView.as_view(), name='signin'),
    path('signup/', views.signup, name='signup'),
    path('logout/', LogoutView.as_view(next_page='main:home'), name='logout'),
]
