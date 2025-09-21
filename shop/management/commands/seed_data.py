from django.core.management.base import BaseCommand
from django.utils.text import slugify
from shop.models import Category  # change 'shop' to your app name


class Command(BaseCommand):
    help = "Seed the Category model with default top-level categories (safe for existing data)."

    def handle(self, *args, **kwargs):
        categories = [
            "Ноутбуки та комп'ютери",
            "Смартфони, ТВ і електротехніка",
            "Товари для геймерів",
            "Побутова техніка",
            "Товари для дому",
            "Інструменти та автотовари",
            "Сантехніка та ремонт",
            "Дача, сад і город",
            "Спорт і захоплення",
            "Одяг, взуття та прикраси",
            "Краса та здоров’я",
            "Дитячі товари",
            "Зоотовари",
            "Офіс, школа, книги",
            "Алкогольні напої та продукти",
            "Побутова хімія",
            "Енергозалежність",
        ]

        created_count = 0
        updated_count = 0

        for name in categories:
            slug = slugify(name)

            # First try to find by slug (to avoid UNIQUE constraint errors)
            category = Category.objects.filter(slug=slug).first()

            if category:
                # If slug exists but name is different, update the name
                if category.name != name:
                    category.name = name
                    category.save()
                    updated_count += 1
            else:
                # If no matching slug, create new
                Category.objects.create(
                    name=name,
                    slug=slug,
                    icon="",
                    parent=None
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ {created_count} categories created, {updated_count} updated."
        ))
