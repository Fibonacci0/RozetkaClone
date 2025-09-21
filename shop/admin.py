from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Promo, Review, Category, User
from django.contrib.auth.admin import UserAdmin

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
            "fields": ("username", "email", "phone_number", "password1", "password2", "is_staff", "is_active")}
        ),
    )

    search_fields = ("email", "phone_number", "username")
    ordering = ("email",)

# from django.urls import path
# from django.shortcuts import render, redirect
# from django import forms
# from django.contrib import messages
# from django.http import HttpResponse
# import csv


# class CSVImportForm(forms.Form):
#     csv_file = forms.FileField()


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
    # def get_urls(self):
    #     urls = super().get_urls()
    #     custom_urls = [
    #         path("import-csv/", self.admin_site.admin_view(self.import_csv), name="product_import_csv"),
    #     ]
    #     return custom_urls + urls

    # def import_csv(self, request):
    #     if request.method == "POST":
    #         form = CSVImportForm(request.POST, request.FILES)
    #         if form.is_valid():
    #             csv_file = form.cleaned_data["csv_file"]
    #             reader = csv.DictReader(csv_file.read().decode("utf-8").splitlines())
    #             count = 0
    #             for row in reader:
    #                 product, created = Product.objects.get_or_create(
    #                     name=row["name"],
    #                     defaults={
    #                         "description": row.get("description", ""),
    #                         "price": row.get("price", 0),
    #                         "slug": row.get("slug", ""),
    #                         "image_url": row.get("image_url", ""),
    #                     },
    #                 )
    #                 if created:
    #                     count += 1
    #             self.message_user(request, f"Imported {count} new products", messages.SUCCESS)
    #             return redirect("..")
    #     else:
    #         form = CSVImportForm()
    #     return render(request, "admin/import_csv.html", {"form": form})
    
    def preview_image(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.get_image())
    preview_image.short_description = "Image"
    
    def display_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    display_categories.short_description = "Categories"
    
    # def export_as_csv(modeladmin, request, queryset):
    #     meta = modeladmin.model._meta
    #     field_names = [field.name for field in meta.fields]

    #     response = HttpResponse(content_type="text/csv")
    #     response["Content-Disposition"] = f"attachment; filename={meta}.csv"
    #     writer = csv.writer(response)

    #     writer.writerow(field_names)
    #     for obj in queryset:
    #         writer.writerow([getattr(obj, field) for field in field_names])
    #     return response

    # export_as_csv.short_description = "Export Selected as CSV"


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

