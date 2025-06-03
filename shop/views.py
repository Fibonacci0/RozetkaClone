from django.shortcuts import render
from .models import Product, Promo  # ОБОВ’ЯЗКОВО

def home(request):
    products = Product.objects.all()
    Promos = Promo.objects.filter(display=True).order_by('-created_at')

    return render(request, 'shop/home.html', {
        'promos': Promos,
        'products': products,})
