from django.shortcuts import render
from catalog.models import Bouquet


def home(request):
    bouquets = Bouquet.objects.all()
    bestsellers = Bouquet.objects.filter(is_bestseller=True)[:4]
    context = {
        'bouquets': bouquets,
        'bestsellers': bestsellers,
    }
    return render(request, 'main/home.html', context)


def about(request):
    return render(request, 'main/about.html')


def payment(request):
    return render(request, 'main/payment.html')
