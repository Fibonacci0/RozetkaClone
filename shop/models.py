from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings

class User(AbstractUser):
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)

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

    image = models.ImageField(upload_to='products/', blank=True, null=True)
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

    def get_image(self):
        if self.image:
            return self.image.url
        return self.image_url

    def __str__(self):
        return self.name



    
class Promo(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # загзука свого зображення
    image = models.ImageField(upload_to='products/', blank=True, null=True)

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
