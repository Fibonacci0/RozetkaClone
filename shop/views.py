from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Category, Product, Promo, Review  # ОБОВ’ЯЗКОВО

from .forms import ProfileEditForm, UserRegisterForm, ReviewForm
from .forms import LoginForm

def home(request):
    products = Product.objects.all()
    promos = Promo.objects.filter(display=True).order_by('-created_at')
    categories = Category.objects.all()

    return render(request, 'shop/home.html', {
        'promos': promos,
        'products': products,
        'categories': categories,
    })

def all_categories(request):
    categories = Category.objects.all()
    return render(request, 'shop/all_categories.html', {'categories': categories})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'shop/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('profile') 

    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST) 
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Вітаємо, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Неправильне ім’я користувача або пароль.")
    else:
        form = LoginForm()

    return render(request, 'shop/login.html', {'form': form})
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'shop/profile.html')


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'shop/profile_edit.html', {'form': form})

def product_detail(request, product_id):
    from django.shortcuts import get_object_or_404
    product = get_object_or_404(Product, id=product_id)

    reviews = product.reviews.select_related('user').order_by('-created_at')
    user_review_exists = False
    
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        other_reviews = reviews.exclude(user=request.user)
        if user_review:
            reviews = [user_review] + list(other_reviews)
            user_review_exists = True


    return render(request, 'shop/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'user_review_exists': user_review_exists
    })


@login_required
def review_form(request, product_id=None, review_id=None):
    if review_id:
        review = get_object_or_404(Review, id=review_id, user=request.user)
        product = get_object_or_404(Product, id=review.product.id)
        is_edit = True
    else:
        review = None
        product = get_object_or_404(Product, id=product_id)
        is_edit = False

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'shop/review_form.html', {
        'form': form,
        'product': product,
        'is_edit': is_edit
        })


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_id = review.product.id

    if request.method == 'POST':
        review.delete()
    return redirect('product_detail', product_id=product_id)

