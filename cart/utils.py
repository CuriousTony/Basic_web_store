from cart.models import Cart


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
            request.session.save()

        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
        request.session['cart_id'] = cart.id

    return cart
