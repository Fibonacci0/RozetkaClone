from django.shortcuts import render, redirect
from .models import Product, Promo, Review  # ОБОВ’ЯЗКОВО
#from django.contrib.auth.decorators import login_required
from .forms import ReviewForm

def home(request):
    products = Product.objects.all()
    promos = Promo.objects.filter(display=True).order_by('-created_at')

    return render(request, 'shop/home.html', {
        'promos': promos,
        'products': products,
    })

def create_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('reviews_list')  # після збереження — перейти на сторінку зі списком
    else:
        form = ReviewForm()
    return render(request, 'shop/create_review.html', {'form': form})


def reviews_list(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'shop/reviews_list.html', {'reviews': reviews})
