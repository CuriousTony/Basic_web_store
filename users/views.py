from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import ensure_csrf_cookie
from cart.utils import get_or_create_cart
from .forms import CustomUserCreationForm
from .forms import CustomLoginForm


class CustomLoginView(LoginView):
    template_name = 'users/signin.html'
    form_class = CustomLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        # Получаем текущую сессионную корзину ДО входа
        session_cart = get_or_create_cart(self.request)
        response = super().form_valid(form)
        user_cart = get_or_create_cart(self.request)

        if session_cart != user_cart:
            user_cart.merge_carts(session_cart)

            if 'cart_id' in self.request.session:
                del self.request.session['cart_id']

        return response


@ensure_csrf_cookie
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})
