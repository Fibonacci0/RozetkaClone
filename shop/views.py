from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Category, Product, Promo
from .forms import ProfileEditForm, LoginForm, UserRegisterForm, ProductFilterForm


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
        form = LoginForm(request, data=request.POST)
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
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})


def product_list(request):
    # Отримуємо всі товари
    products = Product.objects.all()

    # Створюємо форму з GET-параметрів (або None)
    form = ProductFilterForm(request.GET or None)

    # Якщо форма валідна, фільтруємо товари
    if form.is_valid():
        manufacturer = form.cleaned_data.get("manufacturer")
        country = form.cleaned_data.get("country")
        min_price = form.cleaned_data.get("min_price")
        max_price = form.cleaned_data.get("max_price")

        if manufacturer:
            products = products.filter(manufacturer__icontains=manufacturer)
        if country:
            products = products.filter(country__icontains=country)
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)

    # Завжди повертаємо render
    return render(request, "shop/product_list.html", {
        "form": form,
        "products": products
    })

