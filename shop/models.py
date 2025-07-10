from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Optional image upload
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    # Optional external image URL
    image_url = models.URLField(
        max_length=500,
        blank=True,
        default='https://www.shutterstock.com/image-vector/missing-picture-page-website-design-600nw-1552421075.jpg'
    )
    category = models.CharField(max_length=100, blank=True)
    subcategory = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(null=True,max_length=100)  # new
    price = models.DecimalField(max_digits=10, decimal_places=2)
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


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def categories_context(request):
        return {
            'categories': Category.objects.all()
        }

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")

    def __str__(self):
        return f"{self.category.name} / {self.name}"
    
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
