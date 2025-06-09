from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from cart.utils import get_or_create_cart
from cart.models import Cart, CartItem
from .forms import OrderCreateForm
from .models import Order, OrderItem
from users.models import Recipient

User = get_user_model()


def order_create(request):
    cart = get_or_create_cart(request)

    if not cart.items.exists():  # Проверка на пустую корзину
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():  # Используем транзакцию
                    order = form.save(commit=False)
                    order.user = request.user if request.user.is_authenticated else None
                    order.total_price = 0
                    order.save()

                    # Создаем получателя, если получатель - не пользователь
                    if not form.cleaned_data.get('is_recipient_me'):
                        recipient = Recipient.objects.create(
                            user=request.user,
                            name=form.cleaned_data['recipient_name'],
                            phone=form.cleaned_data['recipient_phone'],
                            address=form.cleaned_data.get('recipient_address')
                        )
                        order.recipient = recipient
                        order.save()

                    # Переносим товары из корзины в заказ
                    for item in cart.items.select_related('bouquet'):
                        OrderItem.objects.create(
                            order=order,
                            bouquet=item.bouquet,
                            quantity=item.quantity,
                            price=item.bouquet.price  # Фиксируем цену из каталога
                        )

                    order.update_total()
                    cart.delete()

                    return redirect('orders:order_confirm', order_id=order.id)

            except Exception as e:
                print(f"Ошибка при создании заказа: {str(e)}")
                form.add_error(None, "Ошибка при оформлении заказа")
        else:
            print("Форма не прошла валидацию:", form.errors)
    else:
        initial = {
            'delivery_type': 'delivery',
        }
        form = OrderCreateForm(initial=initial, user=request.user)

    return render(request, 'orders/order_create.html', {
        'form': form,
        'cart': cart
    })


def order_confirm(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    # Дебаг-проверка
    print("Order Items:", order.items.all().values_list('bouquet__name', flat=True))
    print("Total Price:", order.total_price)

    return render(request, 'orders/order_confirm.html', {
        'order': order,
        'order_items': order_items,
        'recipient': order.recipient if hasattr(order, 'recipient') else None,
    })


def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.update_total()
    # Имитация успешной оплаты
    if order.status == 'prepaid':
        order.status = 'pending'
        order.save(update_fields=['status'])
        if hasattr(request.user, 'cart'):
            request.user.cart.items.all().delete()
        return redirect('orders:order_success', order_id=order.id)

    messages.error(request, 'Заказ уже обработан')
    return redirect('orders:order_confirm', order_id=order.id)


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_details.html', {'order': order})


def repeat_order(request, order_id):
    if request.method == 'POST':
        old_order = get_object_or_404(Order, id=order_id, user=request.user)
        cart, created = Cart.objects.get_or_create(user=request.user)

        for item in old_order.items.all():
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                bouquet=item.bouquet,
                defaults={'quantity': item.quantity, 'price': item.bouquet.price}
            )
            if not created:
                cart_item.quantity += item.quantity
                cart_item.save()

        messages.success(request, 'Товары из заказа добавлены в корзину. Пожалуйста, завершите оформление заказа.')
        return redirect('orders:order_create')

    return redirect('orders:order_list')
