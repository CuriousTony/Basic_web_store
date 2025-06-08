from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from catalog.models import Bouquet
from .models import CartItem
from .utils import get_or_create_cart
import json

User = get_user_model()


@require_POST
def add_to_cart(request, bouquet_id):
    try:
        bouquet = Bouquet.objects.get(id=bouquet_id)
        cart = get_or_create_cart(request)
        quantity = int(request.POST.get('quantity', 1))

        cart.add_item(bouquet, quantity)

        return JsonResponse({
            'status': 'success',
            'total_items': cart.items.count(),
            'total_price': str(cart.total_price),
            'bouquet_name': bouquet.name,
            'bouquet_image_url': request.build_absolute_uri(bouquet.pic1.url),
            'bouquet_consists': bouquet.consists,
            'bouquet_price': str(bouquet.price),
        })
    except Bouquet.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Товар не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def cart_detail(request):
    cart = get_or_create_cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


def initiate_order(request):
    """Перенаправление на оформление заказа с обработкой корзины"""
    cart = get_or_create_cart(request)

    if not cart.items.exists():
        return redirect('cart_detail')

    # Сохраняем ID корзины в сессии для последующего использования
    request.session['pending_order_cart'] = cart.id
    return redirect('order_create')


@require_POST
def update_cart_item(request, item_id):
    try:
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)

        data = json.loads(request.body)
        new_quantity = int(data['quantity'])

        if new_quantity <= 0:
            item.delete()
        else:
            item.quantity = new_quantity
            item.save()

        return JsonResponse({
            'status': 'success',
            'total_price': cart.total_price,
            'item_total': item.item_total
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
