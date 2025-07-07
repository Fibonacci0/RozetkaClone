from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Promo, Review  # ОБОВ’ЯЗКОВО
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm

def home(request):
    products = Product.objects.all()
    promos = Promo.objects.filter(display=True).order_by('-created_at')

    return render(request, 'shop/home.html', {
        'promos': promos,
        'products': products,
    })

@login_required
def create_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('reviews_list')
    else:
        form = ReviewForm()
    return render(request, 'shop/create_review.html', {'form': form})


def reviews_list(request):
    reviews = Review.objects.all().order_by('-created_at')
    
    products = Product.objects.all()

    return render(request, 'shop/reviews_list.html', {'reviews': reviews, 'products': products})
