
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator

from django.db.models import Q, Min, Max

from django.http import HttpResponseRedirect, JsonResponse

from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from django.conf import settings

from django.core.mail import send_mail

from django.template.loader import render_to_string

from django.urls import reverse

from .models import Category, Favorite, Product, Promo, Review
from .models import Category, Product, Promo, Review, PhoneOTP, Favorite, Order, OrderItem
from .forms import UserRegisterForm, ReviewForm, LoginForm
from .forms import (
    UserRegisterForm,
    ReviewForm,
    EmailRegisterForm,
    EmailLoginForm,
    PhoneLoginForm,
    PhoneRegisterForm,
    VerifySMSForm,
    PasswordResetRequestForm,
    PasswordResetConfirmForm,
    UserProfileForm,
    PasswordChangeForm,
)
from .utils import generate_sms_code, verify_sms_code
from urllib import request
import random
import json
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from django.db import transaction

User = get_user_model()

def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    
    # promo
    promos = Promo.objects.filter(display=True).order_by('-created_at')

    # Get cart count for display
    cart = request.session.get('cart', {})
    cart_count = sum(int(qty) for qty in cart.values()) if cart else 0
    
    category_slug = request.GET.get('category')
    current_category = None
    if category_slug:
        current_category = Category.objects.filter(slug=category_slug).first()
        if current_category:
            products = products.filter(categories=current_category)

    favorited_ids = set()
    if request.user.is_authenticated:
        favorited_ids = set(
            Favorite.objects.filter(user=request.user)
            .values_list("product_id", flat=True)
        )
        
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
        'promos': promos,
        'selected_brands': selected_brands,
        'selected_countries': selected_countries,
        'selected_sellers': selected_sellers,
        'min_price_selected': min_price_selected,
        'max_price_selected': max_price_selected,
        'min_price': 0,
        'max_price': 100000,
        'favorited_ids': favorited_ids,
        'cart_count': cart_count,  # Add cart count to context

    }
    return render(request, 'shop/home.html', context)

def get_cart_items_with_session(request):
    """Helper function to get cart items from session"""
    cart = request.session.get('cart', {})
    items = []
    total_price = 0
    
    if cart:
        product_ids = [int(pid) for pid in cart.keys()]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
        
        for product_id_str, quantity in cart.items():
            product_id = int(product_id_str)
            product = products.get(product_id)
            if not product:
                continue
                
            quantity = int(quantity)
            price = product.price * quantity
            total_price += price
            
            items.append({
                "product": product,
                "quantity": quantity,
                "price": price,
            })
    
    return items, total_price

@transaction.atomic
def process_payment(request):
    """Process the payment and create order"""
    if request.method != 'POST':
        return redirect('payment_page')
    
    # Get cart items
    items, subtotal = get_cart_items_with_session(request)
    
    if not items:
        messages.error(request, "Ваш кошик порожній")
        return redirect('home')
    
    try:
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        delivery_method = request.POST.get('delivery_method')
        payment_method = request.POST.get('payment_method')
        comments = request.POST.get('comments', '')
        
        # Calculate delivery fee
        delivery_fees = {
            'nova_poshta': Decimal('50.00'),
            'ukr_poshta': Decimal('30.00'),
            'courier': Decimal('100.00'),
        }
        delivery_fee = delivery_fees.get(delivery_method, Decimal('0.00'))
        
        # Apply discount if exists
        discount = request.session.get('cart_discount', 0)
        discount_amount = Decimal(str(subtotal)) * Decimal(str(discount)) / Decimal('100')
        
        # Calculate total
        total = Decimal(str(subtotal)) - discount_amount + delivery_fee
        
        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            delivery_method=delivery_method,
            payment_method=payment_method,
            comments=comments,
            subtotal=Decimal(str(subtotal)),
            delivery_fee=delivery_fee,
            discount_amount=discount_amount,
            total=total,
        )
        
        # Create order items
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )
        
        # Clear cart and discount
        request.session['cart'] = {}
        request.session['cart_discount'] = 0
        request.session.modified = True
        
        # розкоментувати для відправки email
        #send_order_confirmation_email(order)
        
        messages.success(request, f"Замовлення #{order.order_number} успішно оформлено!")
        return redirect('order_success', order_number=order.order_number)
        
    except Exception as e:
        messages.error(request, f"Сталася помилка при оформленні замовлення: {str(e)}")
        return redirect('payment_page')


def order_success(request, order_number):
    """Order success page"""
    order = get_object_or_404(Order, order_number=order_number)
    
    # If user is authenticated, make sure they can only see their own orders
    if request.user.is_authenticated and order.user and order.user != request.user:
        messages.error(request, "Замовлення не знайдено")
        return redirect('home')
    
    return render(request, 'shop/order_success.html', {
        'order': order,
        'categories': Category.objects.all()
    })


@login_required
def order_history(request):
    """User's order history"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    
    return render(request, 'shop/order_history.html', {
        'orders': orders,
        'categories': Category.objects.all()
    })


@login_required
def order_detail(request, order_number):
    """Order detail page"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    return render(request, 'shop/order_detail.html', {
        'order': order,
        'categories': Category.objects.all()
    })


@csrf_exempt
@require_POST
def cart_add_ajax(request):
    """Add item to cart via AJAX"""
    if not request.session.session_key:
        request.session.create()
    
    try:
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        
        # Get product to verify it exists
        product = get_object_or_404(Product, id=product_id)
        
        cart = request.session.get('cart', {})
        
        if product_id in cart:
            cart[product_id] = int(cart[product_id]) + 1
        else:
            cart[product_id] = 1
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'cart_count': sum(cart.values()),
            'message': f'{product.name} додано до кошика'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_POST
def cart_remove_ajax(request):
    """Remove item from cart via AJAX"""
    try:
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        
        cart = request.session.get('cart', {})
        
        if product_id in cart:
            del cart[product_id]
            request.session['cart'] = cart
            request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'cart_count': sum(cart.values())
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_POST
def cart_update_quantity_ajax(request):
    """Update item quantity in cart via AJAX"""
    try:
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        action = data.get('action')  # 'increase' or 'decrease'
        
        cart = request.session.get('cart', {})
        
        if product_id in cart:
            current_quantity = int(cart[product_id])
            
            if action == 'increase':
                cart[product_id] = current_quantity + 1
            elif action == 'decrease' and current_quantity > 1:
                cart[product_id] = current_quantity - 1
            elif action == 'decrease' and current_quantity == 1:
                del cart[product_id]
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'cart_count': sum(cart.values())
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["GET"])
def cart_get_ajax(request):
    """Get current cart contents via AJAX"""
    try:
        items, total_price = get_cart_items_with_session(request)
        
        cart_data = {
            'items': [],
            'total_price': float(total_price),
            'cart_count': sum(item['quantity'] for item in items)
        }
        
        for item in items:
            product = item['product']
            # Get image URL safely
            image_url = '/static/images/default.jpg'
            if hasattr(product, 'image') and product.image:
                image_url = product.image.url
            elif hasattr(product, 'get_image'):
                image_url = product.get_image()
                
            cart_data['items'].append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'quantity': item['quantity'],
                'total': float(item['price']),
                'image': image_url
            })
        
        return JsonResponse(cart_data)
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_POST
def cart_apply_promo_ajax(request):
    """Apply promo code via AJAX"""
    try:
        data = json.loads(request.body)
        promo_code = data.get('promo_code', '').strip().upper()
        
        discount = 0
        message = ""
        
        if promo_code == "SALE10":
            discount = 10
            message = "✅ Промокод застосовано: -10%"
        else:
            message = "❌ Невірний промокод"
        
        # Store discount in session
        request.session['cart_discount'] = discount
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'discount': discount,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def payment_page(request):
    """Updated payment page view"""
    items, total_price = get_cart_items_with_session(request)
    
    if not items:
        messages.error(request, "Ваш кошик порожній")
        return redirect('home')
    
    # Apply discount if exists
    discount = request.session.get('cart_discount', 0)
    discount_amount = 0
    if discount > 0:
        discount_amount = total_price * discount / 100
        total_price = total_price - discount_amount
    
    return render(request, "shop/payment_page.html", {
        "items": items,
        "total_price": total_price,
        "discount": discount,
        "discount_amount": discount_amount,
        "categories": Category.objects.all()
    })

def category_detail(request, slug):
    categories = Category.objects.all()
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(categories=category)

    # promo
    promos = Promo.objects.filter(display=True).order_by('-created_at')

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
        'categories': categories,
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
        'categories': Category.objects.all(),
        'promos': promos,
    }
    return render(request, 'shop/home.html', context)


@login_required
def profile_view(request):
    user = request.user
    warnings = []

    if not user.has_usable_password() and user.email:
        warnings.append({
            'message': 'У вашому акаунті наразі немає пароля для входу. '
                       'Щоб уникнути проблем із входом, рекомендуємо встановити пароль.',
            'link': reverse('profile_password'),
            'type': 'warning'
        })

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)

            for field in ['first_name', 'last_name', 'email', 'phone_number']:
                value = getattr(user, field)
                if value == '':
                    setattr(user, field, None)

            user.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'shop/account/profile.html', {
        'form': form,
        'warnings': warnings,
        })

@login_required
def password_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("profile_password")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "shop/account/password.html", {"form": form})

@login_required
def other_view(request):
    return render(request, "shop/account/other.html")

@login_required
def update_avatar(request):
    if request.method == "POST" and request.FILES.get("avatar"):
        request.user.avatar = request.FILES["avatar"]
        request.user.save()
        messages.success(request, "Аватар оновлено")
    else:
        messages.error(request, "Необхідно вибрати файл")
    return redirect("profile")

# --- Пошук продуктів ---
def search_products(request):
    categories = Category.objects.all()
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        available=True
    )
    return render(request, 'shop/search_results.html', {
        'products': products,
        'query': query,
        'categories': categories,
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

    return render(request, 'shop/login.html', {
        'form': form,
        'categories': Category.objects.all()
    })

# --- Логаут ---
def user_logout(request):
    logout(request)
    return redirect('home')


@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

    if not created:
        favorite.delete()
        return JsonResponse({"favorited": False})
    else:
        return JsonResponse({"favorited": True})
    
@login_required
def product_list(request):
    products = Product.objects.all()

    # which products are favorited by this user?
    favorited_ids = set(
        Favorite.objects.filter(user=request.user).values_list("product_id", flat=True)
    )

    return render(request, "shop/product_list.html", {
        "products": products,
        "favorited_ids": favorited_ids,
    })

# --- Деталі продукту ---
#@login_required
def product_detail(request, product_id):
    categories = Category.objects.all()
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.select_related('user').order_by('-created_at') # type: ignore

    user_review_exists = False
        
    star_counts = {i: reviews.filter(rating=i).count() for i in range(1, 6)}
    total = sum(star_counts.values()) or 1
    star_percentages = {i: (count / total) * 100 for i, count in star_counts.items()}
    
     # Get random products (excluding current product)
    all_products = Product.objects.exclude(id=product.id)
    # Get random products - limit to 4 for display
    if all_products.exists():
        # Convert to list and shuffle for random selection
        products_list = list(all_products)
        random.shuffle(products_list)
        random_products = products_list[:4]  # Get first 4 after shuffle
    else:
        random_products = []
        
        
    if request.user.is_authenticated:
        # check if current user liked it
        is_favorited = Favorite.objects.filter(user=request.user, product=product).exists()

        # reviews logic
        user_review = reviews.filter(user=request.user).first()
        other_reviews = reviews.exclude(user=request.user)
        if user_review:
            reviews = [user_review] + list(other_reviews)
            user_review_exists = True
    else:
        is_favorited = False

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'user_review_exists': user_review_exists,
        'categories': categories,
        'is_favorited': is_favorited,
        "star_counts": star_counts,
        "star_percentages": star_percentages,
        'random_products': random_products,
    })


# --- Форма відгуку ---
@login_required
def review_form(request, product_id=None, review_id=None):
    user_email = request.user.email if request.user.is_authenticated else ""
    product = get_object_or_404(Product, id=product_id) if product_id else None
    # Маскуємо email: 3 символи + ***
    masked_email = ""
    if user_email and "@" in user_email:
        name, domain = user_email.split("@", 1)
        masked_email = f"{name[:3]}***@{domain}"
    if review_id:
        review = get_object_or_404(Review, id=review_id, user=request.user)
        product = get_object_or_404(Product, id=review.product.id) # type: ignore
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
            return redirect('product_detail', product_id=product.id) # type: ignore
    else:
        form = ReviewForm(instance=review)

    return render(request, 'shop/review_form.html', {
        'form': form,
        'product': product,
        'masked_email': masked_email,
        'is_edit': is_edit
    })

# --- Видалення відгуку ---
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_id = review.product.id # type: ignore

    if request.method == 'POST':
        review.delete()
    return redirect('product_detail', product_id=product_id)


def register_email(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = EmailRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='shop.backends.EmailBackend')
            return redirect('home')
    else:
        form = EmailRegisterForm()

    return render(request, 'shop/auth.html', {'form': form})

def login_email(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return redirect('home')
    else:
        form = EmailLoginForm()

    return render(request, 'shop/auth.html', {'form': form})

def login_phone_request(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == "POST":
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone"]
            user = User.objects.get(phone_number=phone)

            generate_sms_code(user)
            now = timezone.now()

            active_code = PhoneOTP.objects.filter(user=user, expires_at__gte=now).first()
            if active_code:
                request.session["otp_expires_at"] = active_code.expires_at.isoformat()

            request.session["phone_user_id"] = user.id # type: ignore
            request.session["phone_number"] = phone
            request.session.modified = True

            return redirect("verify_phone_code")
    else:
        form = PhoneLoginForm()
    return render(request, "shop/auth.html", {"form": form})

def register_phone_request(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == "POST":
        form = PhoneRegisterForm(request.POST)
        if form.is_valid():
            phone_clean = form.cleaned_data["phone"]

            user = User.objects.create_user(
                username = phone_clean,
                phone_number = phone_clean,
            )

            user.email = None
            user.save(update_fields=['email'])

            generate_sms_code(user)

            request.session["phone_user_id"] = user.id
            request.session["phone_number"] = phone_clean
            request.session.modified = True

            return redirect("verify_phone_code")
    else:
        form = PhoneRegisterForm()
    return render(request, "shop/auth.html", {"form": form})

def verify_phone_code(request):
    user_id = request.session.get("phone_user_id")
    phone_number = request.session.get("phone_number")
    otp_expires_at = request.session.get("otp_expires_at")
    
    print(f"DEBUG: otp_expires_at -> {otp_expires_at}") # test

    if not user_id:
        return redirect("login_phone_request")

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        form = VerifySMSForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            if verify_sms_code(user, code):
                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                return redirect("home")
            else:
                form.add_error("code", "Невірний або прострочений код")
    else:
        form = VerifySMSForm()
    return render(request, "shop/verify_sms_code.html", {"form": form, "phone_number": phone_number, "otp_expires_at": otp_expires_at,})

def resend_sms(request):
    user_id = request.session.get("phone_user_id")

    if not user_id:
        return JsonResponse({"success": False, "error": "Користувач не знайдений"}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"success": False, "error": "Користувач не існує"}, status=400)

    generate_sms_code(user)
    now = timezone.now()
    active_code = PhoneOTP.objects.filter(user=user, expires_at__gte=now).first()

    if active_code:
        request.session["otp_expires_at"] = active_code.expires_at.isoformat()
        request.session.modified = True
        return JsonResponse({"success": True, "expires_at": active_code.expires_at.isoformat()})

    return JsonResponse({"success": False, "error": "Не вдалося надіслати код"}, status=400)

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.get(email=email)

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_link = request.build_absolute_uri(f"/reset/{uid}/{token}/")

            html_message = render_to_string("emails/password_reset.html", {"reset_link": reset_link})

            send_mail(
                subject="Відновлення паролю",
                message="Відкрийте лист для відновлення паролю", 
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
                html_message=html_message
            )

            return render(request, "shop/password_reset.html", {"step": "done"})
    else:
        form = PasswordResetRequestForm()

    return render(request, "shop/password_reset.html", {"form": form, "step": "request" })

def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if not user or not default_token_generator.check_token(user, token):
        form = PasswordResetConfirmForm()
        return render(request, "shop/password_reset.html", {
            "step": "confirm",
            "form": form,
            "validlink": False
        })
    
    if request.method == "POST":
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            new_password = request.POST.get("password")
            user.password = make_password(new_password)
            user.save()
            return render(request, "shop/password_reset.html", {"step": "complete"})
    else:
        form = PasswordResetConfirmForm()
        
    return render(request, "shop/password_reset.html", {"step": "confirm", "form": form})


def add_to_cart(request, product_id):
    if not request.session.session_key:
        request.session.create()

    cart = request.session.get('cart', [])

    # шукаємо продукт в кошику
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += 1
            break
    else:
        cart.append({'id': product_id, 'quantity': 1})

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_page')



def get_cart_items(request):
    cart = request.session.get('cart', [])
    items = []
    total_price = 0

    product_ids = [int(item["id"]) for item in cart]
    products = {p.id: p for p in Product.objects.filter(id__in=product_ids)} # type: ignore

    for item in cart:
        product_id = int(item["id"])
        product = products.get(product_id)
        if not product:
            continue  # якщо товар видалено з БД
        quantity = int(item.get("quantity", 1))
        price = product.price * quantity
        total_price += price
        items.append({
            "product": product,
            "quantity": quantity,
            "price": price,
        })

    return items, total_price


def cart_json(request):
    items, total_price = get_cart_items(request)
    data = {
        "items": [
            {
                "id": item["product"].id,
                "name": item["product"].name,
                "price": item["product"].price,
                "quantity": item["quantity"],
                "total": item["price"],
                "image": item["product"].get_image,
            }
            for item in items
        ],
        "total_price": total_price,
    }
    return JsonResponse(data)

def cart_remove(request, pk):
    cart = request.session.get('cart', [])
    pk = int(pk)

    # видаляємо товар з кошика
    cart = [item for item in cart if int(item["id"]) != pk]

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('payment_page')

@login_required
def favorites_list(request):
    """Повертає JSON зі всіма улюбленими товарами користувача"""
    favorites = Favorite.objects.filter(user=request.user).select_related("product")
    items = [
        {
            "id": f.product.id,
            "name": f.product.name,
            "price": f.product.price,
            "image": f.product.get_image() if hasattr(f.product, "get_image") else "",
        }
        for f in favorites
    ]
    return JsonResponse({"items": items})