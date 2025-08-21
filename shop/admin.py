from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Promo, Review, Category

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'price', 'available', 'created_at', 'display_categories', 'rating', 'preview_image'
    )
    list_filter = ('available', 'created_at', 'categories')
    search_fields = ('name', 'description', 'categories__name')
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ('created_at', 'preview_image')
    fields = (
        'name', 'description', 'image', 'image_url', 'categories', 'slug',
        'price', 'available', 'rating', 'review_count', 'created_at', 'preview_image'
    )

    def preview_image(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.get_image())
    preview_image.short_description = "Image"
    
    def display_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    display_categories.short_description = "Categories"


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('name', 'display', 'created_at', 'preview_image')
    list_filter = ('display', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'preview_image')
    fields = ('name', 'description', 'image', 'image_url', 'display', 'created_at', 'preview_image')

    def preview_image(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.get_image())
    preview_image.short_description = "Image"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'text')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'icon')
    search_fields = ('name',)
    list_filter = ('parent',)
    prepopulated_fields = {"slug": ("name",)}

