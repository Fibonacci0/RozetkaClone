from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin

from .models import (
    Order, OrderItem, Product, Promo, Review, Category,
    User, Favorite, PhoneOTP
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("username", "email", "phone_number", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "phone_number")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "phone_number", "password1", "password2", "is_staff", "is_active"),
        }),
    )

    search_fields = ("username", "email", "phone_number")
    ordering = ("username",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'price', 'available', 'created_at',
        'display_categories', 'rating', 'preview_image'
    )
    list_filter = ('available', 'created_at', 'categories', 'brand', 'country', 'seller')
    search_fields = ('name', 'description', 'categories__name', 'brand', 'country', 'seller')
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ('created_at', 'preview_image')
    fields = (
        'name', 'description', 'image', 'image_url', 'categories', 'slug',
        'price', 'brand', 'country', 'seller', 'size',
        'is_popular', 'available',
        'rating', 'review_count', 'created_at', 'preview_image'
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
    search_fields = ('product__name', 'user__username', 'comment')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'icon')
    search_fields = ('name',)
    list_filter = ('parent',)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "first_name",
        "last_name",
        "email",
        "phone",
        "total",
        "status",
        "is_paid",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "is_paid", "delivery_method", "payment_method", "created_at")
    search_fields = ("order_number", "first_name", "last_name", "email", "phone")
    readonly_fields = ("created_at", "updated_at", "paid_at")
    ordering = ("-created_at",)

    fieldsets = (
        ("Order Info", {
            "fields": (
                "order_number",
                "user",
                "status",
                "created_at",
                "updated_at",
            )
        }),
        ("Customer Details", {
            "fields": (
                "first_name",
                "last_name",
                "email",
                "phone",
                "address",
            )
        }),
        ("Order Details", {
            "fields": (
                "delivery_method",
                "payment_method",
                "comments",
            )
        }),
        ("Pricing", {
            "fields": (
                "subtotal",
                "delivery_fee",
                "discount_amount",
                "total",
            )
        }),
        ("Payment", {
            "fields": (
                "is_paid",
                "paid_at",
            )
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'get_total_price']
    list_filter = ['order__created_at']
    search_fields = ['order__order_number', 'product__name']
    
    def get_total_price(self, obj):
        return f"{obj.total_price} ₴"
    get_total_price.short_description = 'Загальна сума'
# @admin.register(Favorite)
# class FavoriteAdmin(admin.ModelAdmin):
#     list_display = ('user', 'product', 'created_at')
#     list_filter = ('created_at',)
#     search_fields = ('user__username', 'product__name')


# @admin.register(PhoneOTP)
# class PhoneOTPAdmin(admin.ModelAdmin):
#     list_display = ('user', 'code', 'created_at', 'expires_at', 'is_valid_status')
#     list_filter = ('created_at', 'expires_at')
#     search_fields = ('user__username', 'code')

#     def is_valid_status(self, obj):
#         return obj.is_valid()
#     is_valid_status.boolean = True
#     is_valid_status.short_description = "Is Valid?"
#     readonly_fields = ('created_at', 'expires_at', 'is_valid_status')