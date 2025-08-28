from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, FilterOption

@receiver(post_save, sender=Product)
def create_filters_for_product(sender, instance, created, **kwargs):
    if created:
        # Створюємо фільтр для категорії
        if instance.category:
            FilterOption.objects.get_or_create(
                name=instance.category.name,
                category=instance.category
            )
        # Створюємо фільтр для підкатегорії
        if instance.subcategory:
            FilterOption.objects.get_or_create(
                name=instance.subcategory.name,
                subcategory=instance.subcategory
            )
