from django.shortcuts import render
from urllib import request
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db.models import Q, Max  # <- додав сюди Max
from django.db.models import Min, Max
from .models import Category, Favorite, Product, Promo, Review
from django.conf import settings
from .utils import generate_sms_code, verify_sms_code
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string
from .models import Category, Product, Promo, Review, PhoneOTP
from .forms import ReviewForm, EmailRegisterForm, EmailLoginForm, PhoneLoginForm, PhoneRegisterForm, VerifySMSForm, PasswordResetRequestForm, PasswordResetConfirmForm, UserProfileForm, PasswordChangeForm
from django.urls import reverse

from django.contrib.auth import update_session_auth_hash

from django.http import HttpResponseRedirect, JsonResponse

User = get_user_model()

def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    
    # promo
    promos = Promo.objects.filter(display=True).order_by('-created_at')


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
    }
    return render(request, 'shop/home.html', context)


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

# --- Логаут ---
def user_logout(request):
    logout(request)
    return redirect('home')

# --- Профіль ---
@login_required
def profile_view(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    user_obj = User.objects.get(id=request.user.id)
    phone_number = getattr(user_obj, 'phone_number', None)
        
    favorites = Favorite.objects.filter(user=request.user).select_related("product")
    return render(request, "shop/profile.html", {
        "favorites": favorites,
        "categories": categories,
        "products": products,
        "phone_number": phone_number,
    })

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
@login_required
def product_detail(request, product_id):
    categories = Category.objects.all()
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.select_related('user').order_by('-created_at') # type: ignore

    user_review_exists = False
    is_favorited = False

    if request.user.is_authenticated:
        # check if current user liked it
        is_favorited = Favorite.objects.filter(user=request.user, product=product).exists()

        # reviews logic
        user_review = reviews.filter(user=request.user).first()
        other_reviews = reviews.exclude(user=request.user)
        if user_review:
            reviews = [user_review] + list(other_reviews)
            user_review_exists = True

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'user_review_exists': user_review_exists,
        'categories': categories,
        'is_favorited': is_favorited,
    })


# --- Форма відгуку ---
@login_required
def review_form(request, product_id=None, review_id=None):
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



# def payment_page(request):
#     cart = request.session.get('cart', [])
#     return render(request, 'shop/payment_page.html', {'cart': cart})

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
    cart = request.session.get('cart', [])
    cart.append({'id': product_id, 'quantity': 1})
    request.session['cart'] = cart
    return redirect('cart_page')

@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related("product")
    items = []
    for fav in favorites:
        product = fav.product
        items.append({
            "id": product.id,
            "name": product.name,
            "price": str(product.price),
            "image": product.get_image() if hasattr(product, "get_image") else (product.image.url if product.image else None),
        })
    return JsonResponse({"items": items})

def payment_page(request):
    cart = request.session.get('cart', [])
    products = []
    total = 0

    for item in cart:
        try:
            product = Product.objects.get(id=item['id'])
            quantity = item.get('quantity', 1)
            subtotal = product.price * quantity
            total += subtotal
            products.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            continue

    context = {
        "products": products,
        "total": total,
    }
    return render(request, "shop/payment_page.html", context)


