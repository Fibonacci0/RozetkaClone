from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Promo

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'available', 'created_at', 'preview_image')
    fields = ('name', 'description', 'image', 'image_url', 'price', 'available')

    class Media:
        css = {
            'all': ('css/custom_admin.css',)  # шлях до вашого CSS у static
        }
        js = (
            # якщо потрібні якісь JS файли, вказуйте тут
        )

    def preview_image(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.get_image())

    preview_image.short_description = "Image"


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('name', 'display', 'created_at', 'preview_image')
    fields = ('name', 'display', 'image', 'image_url', 'created_at')

    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    def preview_image(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.get_image())

    preview_image.short_description = "Image"
