from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import Review, Product, Promo
from django.contrib.auth import get_user_model

User = get_user_model()

def update_product_rating(product):
    reviews = product.reviews.all()
    total_reviews = reviews.count()
    if (total_reviews > 0):
        avg_rating = sum([r.rating for r in reviews]) / total_reviews
    else:
        avg_rating = 0

    product.rating = round(avg_rating, 2)
    product.review_count = total_reviews
    product.save()


@receiver(post_save, sender=Review)
def handle_review_save(sender, instance, **kwards):
    update_product_rating(instance.product)

@receiver(post_delete, sender=Review)
def handle_review_delete(sender, instance, **kwards):
    update_product_rating(instance.product)

@receiver(pre_save, sender=User)
def delete_old_avatar_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_file = sender.objects.get(pk=instance.pk).avatar
    except sender.DoesNotExist:
        return
    new_file = instance.avatar
    if old_file and old_file != new_file:
        old_file.delete(save=False)

@receiver(post_delete, sender=User)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    if instance.avatar:
        instance.avatar.delete(save=False)

@receiver(pre_save, sender=Product)
def delete_old_product_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_file = sender.objects.get(pk=instance.pk).image
    except sender.DoesNotExist:
        return
    new_file = instance.image
    if old_file and old_file != new_file:
        old_file.delete(save=False)

@receiver(post_delete, sender=Product)
def delete_product_image_on_delete(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)

@receiver(pre_save, sender=Promo)
def delete_old_promo_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_file = sender.objects.get(pk=instance.pk).image
    except sender.DoesNotExist:
        return
    new_file = instance.image
    if old_file and old_file != new_file:
        old_file.delete(save=False)

@receiver(post_delete, sender=Promo)
def delete_promo_photo_on_delete(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)
