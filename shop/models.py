from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")

    def __str__(self):
        return f"{self.category.name} / {self.name}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Зображення
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(
        max_length=500,
        blank=True,
        default='https://www.shutterstock.com/image-vector/missing-picture-page-website-design-600nw-1552421075.jpg'
    )

    # Категорії
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="products",
        null=True,
        blank=True
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        related_name="products",
        null=True,
        blank=True
    )
    slug = models.SlugField(null=True, max_length=100)

    # Базові атрибути
    manufacturer = models.CharField(max_length=100, blank=True, default="Не вказано")
    country = models.CharField(max_length=100, blank=True, default="Не вказано")
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


# ------------------- Адаптивні фільтри -------------------
class FilterOption(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="filters", null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="filters", null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.category or self.subcategory})"


class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="attributes")
    filter_option = models.ForeignKey(FilterOption, on_delete=models.CASCADE, related_name="attributes")
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.product.name} – {self.filter_option.name}: {self.value}"


# ------------------- Відгуки -------------------
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name} ({self.rating}★)"


# ------------------- Промо -------------------
class Promo(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
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
