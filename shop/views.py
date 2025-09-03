from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db.models import Q, Max  # <- додав сюди Max
from django.db.models import Min, Max
from .models import Category, Product, Promo, Review
from .forms import ProfileEditForm, UserRegisterForm, ReviewForm, LoginForm
from django.conf import settings
from django.http import HttpResponseRedirect


def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    category_slug = request.GET.get('category')
    current_category = None
    if category_slug:
        current_category = Category.objects.filter(slug=category_slug).first()
        if current_category:
            products = products.filter(categories=current_category)

    # Фільтри
    selected_brands = request.GET.getlist('brand')
    selected_countries = request.GET.getlist('country')
    selected_sellers = request.GET.getlist('seller')
    min_price_selected = request.GET.get('min_price')
    max_price_selected = request.GET.get('max_price')

    # Безпечний парсинг
    try:
        min_price_selected = int(min_price_selected)
        if min_price_selected < 0:
            min_price_selected = 0
    except (TypeError, ValueError):
        min_price_selected = 0

    try:
        max_price_selected = int(max_price_selected)
        if max_price_selected > 100000:
            max_price_selected = 100000
    except (TypeError, ValueError):
        max_price_selected = 100000

    # Фільтрація
    if selected_brands:
        products = products.filter(brand__in=selected_brands)
    if selected_countries:
        products = products.filter(country__in=selected_countries)
    if selected_sellers:
        products = products.filter(seller__in=selected_sellers)
    
    # Фільтр по ціні
    products = products.filter(price__gte=min_price_selected, price__lte=max_price_selected)

    context = {
        'categories': categories,
        'products': products,
        'current_category': current_category,
        'brands': Product.objects.values_list('brand', flat=True).distinct(),
        'countries': Product.objects.values_list('country', flat=True).distinct(),
        'sellers': Product.objects.values_list('seller', flat=True).distinct(),
        'selected_brands': selected_brands,
        'selected_countries': selected_countries,
        'selected_sellers': selected_sellers,
        'min_price_selected': min_price_selected,
        'max_price_selected': max_price_selected,
        'min_price': 0,
        'max_price': 100000,
    }
    return render(request, 'shop/home.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(categories=category)

    selected_brands = request.GET.getlist('brand')
    selected_countries = request.GET.getlist('country')
    selected_sellers = request.GET.getlist('seller')
    min_price_selected = request.GET.get('min_price')
    max_price_selected = request.GET.get('max_price')

    try:
        min_price_selected = int(min_price_selected)
        if min_price_selected < 0:
            min_price_selected = 0
    except (TypeError, ValueError):
        min_price_selected = 0

    try:
        max_price_selected = int(max_price_selected)
        if max_price_selected > 100000:
            max_price_selected = 100000
    except (TypeError, ValueError):
        max_price_selected = 100000

    if selected_brands:
        products = products.filter(brand__in=selected_brands)
    if selected_countries:
        products = products.filter(country__in=selected_countries)
    if selected_sellers:
        products = products.filter(seller__in=selected_sellers)

    products = products.filter(price__gte=min_price_selected, price__lte=max_price_selected)

    context = {
        'current_category': category,
        'products': products,
        'brands': Product.objects.values_list('brand', flat=True).distinct(),
        'countries': Product.objects.values_list('country', flat=True).distinct(),
        'sellers': Product.objects.values_list('seller', flat=True).distinct(),
        'selected_brands': selected_brands,
        'selected_countries': selected_countries,
        'selected_sellers': selected_sellers,
        'min_price_selected': min_price_selected,
        'max_price_selected': max_price_selected,
        'min_price': 0,
        'max_price': 100000,
    }
    return render(request, 'shop/home.html', context)


# --- Пошук продуктів ---
def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        available=True
    )
    return render(request, 'shop/search_results.html', {
        'products': products,
        'query': query
    })

# --- Всі категорії ---
def all_categories(request):
    categories = Category.objects.all()
    return render(request, 'shop/all_categories.html', {'categories': categories})

# --- Реєстрація користувача ---
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

# --- Логін користувача ---
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

# --- Логаут ---
def user_logout(request):
    logout(request)
    return redirect('home')

# --- Профіль ---
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

# --- Деталі продукту ---
def product_detail(request, product_id):
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

# --- Форма відгуку ---
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

# --- Видалення відгуку ---
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_id = review.product.id

    if request.method == 'POST':
        review.delete()
    return redirect('product_detail', product_id=product_id)


def pay(request):
    jar_url = getattr(
        settings,
        'MONOBANK_JAR_URL',
        'https://send.monobank.ua/jar/7Fn8uoXAXJ'
    )
    return HttpResponseRedirect(jar_url)









