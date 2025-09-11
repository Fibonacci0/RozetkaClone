from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q
from .models import Category, Product, Promo, Review, PhoneOTP
from .forms import ProfileEditForm, UserRegisterForm, ReviewForm, EmailRegisterForm, EmailLoginForm, PhoneLoginForm, VerifySMSForm, PasswordResetRequestForm, PasswordResetConfirmForm
from .forms import LoginForm
from .utils import generate_sms_code, verify_sms_code
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string

User = get_user_model()


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

def home(request):
    products = Product.objects.all()
    promos = Promo.objects.filter(display=True).order_by('-created_at')
    categories = Category.objects.all()

    return render(request, 'shop/home.html', {
        'promos': promos,
        'products': products,
        'categories': categories,
    })

def home(request, category_slug=None):
    promos = Promo.objects.filter(display=True).order_by('-created_at')
    categories = Category.objects.filter(parent__isnull=True)
    current_category = None
    products = Product.objects.all()

    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        categories = current_category.children.all()
        category_ids = [current_category.id] + list(current_category.children.values_list('id', flat=True))
        products = Product.objects.filter(categories__id__in=category_ids).distinct()

    return render(request, 'shop/home.html', {
        'promos': promos,
        'categories': categories,
        'current_category': current_category,
        'products': products,
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

    # return render(request, 'shop/login.html', {'form': form})
    return render(request, 'shop/auth.html', {'form': form})


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
    if request.method == "POST":
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone"]
            try:
                user = User.objects.get(phone_number=phone)
            except User.DoesNotExist:
                form.add_error("phone", "Користувача з таким номером не існує")
                return render(request, "shop/auth.html", {"form": form})

            generate_sms_code(user)
            now = timezone.now()

            active_code = PhoneOTP.objects.filter(user=user, expires_at__gte=now).first()
            if active_code:
                request.session["otp_expires_at"] = active_code.expires_at.isoformat()

            request.session["phone_user_id"] = user.id
            request.session["phone_number"] = phone
            request.session.modified = True


            return redirect("verify_phone_code")
    else:
        form = PhoneLoginForm()
    return render(request, "shop/auth.html", {"form": form})

def register_phone_request(request):
    if request.method == "POST":
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone"]
            if User.objects.filter(phone_number=phone).exists():
                form.add_error("phone", "Користувач з таким номером вже існує")
                return render(request, "shop/auth.html", {"form": form})

            user = User.objects.create_user(username=phone, phone_number=phone)

            generate_sms_code(user)
            request.session["phone_user_id"] = user.id
            request.session["phone_number"] = phone
            
            return redirect("verify_phone_code")
    else:
        form = PhoneLoginForm()
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
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return render(request, "shop/password_reset.html", {"error": "Користувача не знайдено", "step": "done"})

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

    if user and default_token_generator.check_token(user, token):
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
    else:
        form = PasswordResetConfirmForm()
        return render(request, "shop/password_reset.html", {"step": "confirm", "form": form, "validlink": False})

    


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

