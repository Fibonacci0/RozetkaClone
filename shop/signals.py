from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review, Product

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
