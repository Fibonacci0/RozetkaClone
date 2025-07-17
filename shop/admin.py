

from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Promo

# Приклад модельки
#admin.site.register([])  # Register your models here, e.g., admin.site.register(MyModel)

# кастомні модельки
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'available', 'created_at', 'preview_image')
    fields = ('name', 'description', 'image', 'image_url', 'price', 'available')

    def preview_image(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.get_image())

    preview_image.short_description = "Image"


@admin.register(Promo)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'display', 'created_at', 'preview_image')
    fields = ('name', 'display', 'image', 'image_url', 'created_at')

    def preview_image(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.get_image())

    preview_image.short_description = "Image"
