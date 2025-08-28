from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Product, Category, SubCategory, Promo, ProductAttribute
from .forms import (
    DynamicProductFilterForm,
    LoginForm,
    UserRegisterForm,
    ProfileEditForm,
    ProductForm,
    ProductAttributeFormSet
)


def home(request):
    products = Product.objects.all()
    promos = Promo.objects.filter(display=True).order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'shop/home.html', {
        'promos': promos,
        'products': products,
        'categories': categories,
    })


def product_list(request, category_slug=None, subcategory_slug=None):
    category = None
    subcategory = None
    products = Product.objects.all()

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    if subcategory_slug:
        subcategory = get_object_or_404(SubCategory, slug=subcategory_slug)
        products = products.filter(subcategory=subcategory)

    # ------------------- Фільтри -------------------
    filter_form = DynamicProductFilterForm(category=category, subcategory=subcategory, data=request.GET or None)
    if filter_form.is_valid():
        cd = filter_form.cleaned_data
        if cd.get('manufacturer'):
            products = products.filter(manufacturer__icontains=cd['manufacturer'])
        if cd.get('country'):
            products = products.filter(country__icontains=cd['country'])
        if cd.get('min_price') is not None:
            products = products.filter(price__gte=cd['min_price'])
        if cd.get('max_price') is not None:
            products = products.filter(price__lte=cd['max_price'])
        if cd.get('available'):
            products = products.filter(available=True)

        # Виправлено динамічні атрибути
        for field_name, value in cd.items():
            if field_name.startswith('attr_') and value:
                attr_name = field_name[5:].replace('_', ' ')
                products = products.filter(
                    attributes__filter_option__name__iexact=attr_name,
                    attributes__value__icontains=value
                )

    # ------------------- Додавання нового товару -------------------
    if request.method == 'POST' and 'add_product' in request.POST:
        product_form = ProductForm(request.POST, request.FILES)
        attr_form = ProductAttributeFormSet(request.POST)
        if product_form.is_valid() and attr_form.is_valid():
            product = product_form.save()
            attr_form.instance = product
            attr_form.save()
            messages.success(request, f"Товар '{product.name}' додано!")
            return redirect('product_list')
    else:
        product_form = ProductForm()
        attr_form = ProductAttributeFormSet()

    return render(request, "shop/product_list.html", {
        'category': category,
        'subcategory': subcategory,
        'products': products.distinct(),
        'form': filter_form,
        'product_form': product_form,
        'attr_form': attr_form,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})


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
        return redirect('home')

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


def all_categories(request):
    categories = Category.objects.all()
    return render(request, 'shop/all_categories.html', {'categories': categories})
