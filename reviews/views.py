from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order
from catalog.models import Bouquet
from .forms import ReviewForm
from .models import Review


def reviews(request):
    approved_reviews = Review.objects.filter(is_approved=True).order_by('-created_at')
    return render(request, 'reviews/reviews.html', {'reviews': approved_reviews})


@login_required
def add_review(request, order_id, bouquet_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    bouquet = get_object_or_404(Bouquet, id=bouquet_id)

    # Проверки перед созданием отзыва
    if order.status != 'completed':
        messages.error(request, 'Отзыв можно оставить только для завершённых заказов.')
        return redirect('orders:order_details', order_id=order.id)

    if Review.objects.filter(user=request.user, bouquet=bouquet).exists():
        messages.error(request, 'Вы уже оставили отзыв на этот букет.')
        return redirect('orders:order_details', order_id=order.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, order=order, bouquet=bouquet)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.bouquet = bouquet
            review.order = order
            review.save()
            messages.success(request, 'Отзыв успешно сохранён!')
            return redirect('orders:order_details', order_id=order.id)
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = ReviewForm()

    return render(request, 'reviews/add_review.html', {
        'form': form,
        'bouquet': bouquet,
        'order': order
    })
