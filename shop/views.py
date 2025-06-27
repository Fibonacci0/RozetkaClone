from django.shortcuts import render
from .models import Product  # ОБОВ’ЯЗКОВО

def home(request):
    products = Product.objects.all()
    return render(request, 'shop/home.html', {'products': products})

def user(request):
    products = Product.objects.all()
    return render(request, 'shop/user.html', {'products': products})
