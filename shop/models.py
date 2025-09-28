import uuid
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User, AbstractUser # type: ignore
from django.conf import settings
from .azure_storage import AvatarStorage, ProductStorage, PromoStorage

class User(AbstractUser):
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=15, blank=True, null=True)
    last_name = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(storage=AvatarStorage, blank=True, null=True)
    #saved_cart = models.JSONField(default=list, blank=True)



class PhoneOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() <= self.expires_at

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Вкажи клас іконки"
    )

    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        related_name='children', 
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return " / ".join(full_path[::-1])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    id = models.AutoField(primary_key=True)

    image = models.ImageField(storage=ProductStorage, blank=True, null=True)
    image_url = models.URLField(
        max_length=500,
        blank=True,
        default='https://www.shutterstock.com/image-vector/missing-picture-page-website-design-600nw-1552421075.jpg'
    )

    categories = models.ManyToManyField("Category", related_name='products')
    slug = models.SlugField(null=True, max_length=100)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.CharField(max_length=100, blank=True, null=True)   
    country = models.CharField(max_length=100, blank=True, null=True) 
    seller = models.CharField(max_length=100, blank=True, null=True)  

    # Нове поле для розміру
    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    ]
    size = models.CharField(max_length=3, choices=SIZE_CHOICES, blank=True, null=True)

    is_popular = models.BooleanField(default=False)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    rating = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)
    #in_stock = models.BooleanField(default=True)


    def get_image(self):
        if self.image:
            return self.image.url
        return self.image_url

    def __str__(self):
        return self.name
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')


    
class Promo(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # загзука свого зображення
    image = models.ImageField(storage=PromoStorage, blank=True, null=True)

    # URL
    image_url = models.URLField(
        max_length=500,
        blank=True,
        default='https://www.shutterstock.com/image-vector/missing-picture-page-website-design-600nw-1552421075.jpg'
    )
    display = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def get_image(self):
        if self.image:
            return self.image.url
        return self.image_url

    def __str__(self):
        return self.name

class Order(models.Model):
    DELIVERY_CHOICES = [
        ('nova_poshta', 'Нова Пошта'),
        ('ukr_poshta', 'Укрпошта'),
        ('courier', 'Кур\'єрська доставка'),
    ]
    
    PAYMENT_CHOICES = [
        ('cash_on_delivery', 'Оплата при отриманні'),
        ('card', 'Оплата карткою'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Очікує обробки'),
        ('confirmed', 'Підтверджено'),
        ('processing', 'В обробці'),
        ('shipped', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Скасовано'),
    ]

    # Order identification
    order_number = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Customer information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    
    # Order details
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    comments = models.TextField(blank=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    

    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.first_name} {self.last_name}"
    
    def get_status_display_color(self):
        """Return Bootstrap color class for status"""
        colors = {
            'pending': 'warning',
            'confirmed': 'info',
            'processing': 'primary',
            'shipped': 'success',
            'delivered': 'success',
            'cancelled': 'danger',
        }
        return colors.get(self.status, 'secondary')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} for Order #{self.order.order_number}"
    
    @property
    def total_price(self):
        return self.quantity * self.price

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    advantages = models.TextField(blank=True)
    disadvantages = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.rating}★ для {self.product.name}"

