from django.shortcuts import render
from .models import Product, Promo  # ОБОВ’ЯЗКОВО
#from django.contrib.auth.decorators import login_required

def home(request):
    products = Product.objects.all()
    promos = Promo.objects.filter(display=True).order_by('-created_at')

    return render(request, 'shop/home.html', {
        'promos': promos,
        'products': products,
    })

