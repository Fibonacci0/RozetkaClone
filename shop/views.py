from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Category, Product, Promo  # ОБОВ’ЯЗКОВО

from .forms import ProfileEditForm, LoginForm, UserRegisterForm  # Імпортуємо форму для редагування профілю

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
    return render(request, 'shop/product_detail.html', {'product': product})
