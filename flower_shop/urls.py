from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('main.urls', 'main'), namespace='main')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('orders/', include(('orders.urls', 'orders'), namespace='orders')),
    path('cart/', include(('cart.urls', 'cart'), namespace='cart')),
    path('reviews/', include('reviews.urls')),
    path('analytics/', include('analytics.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
