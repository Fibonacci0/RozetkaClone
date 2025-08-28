from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import Product, ProductAttribute, FilterOption


# ------------------- Форма входу -------------------
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg",
            "placeholder": "Ім'я користувача"
        }),
        label="Логін"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg",
            "placeholder": "Пароль"
        }),
        label="Пароль"
    )


# ------------------- Форма реєстрації -------------------
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg",
            "placeholder": "Email"
        }),
        label="Email"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


# ------------------- Форма редагування профілю -------------------
class ProfileEditForm(UserChangeForm):
    password = None  # Приховати поле пароля

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


# ------------------- Динамічна адаптивна форма фільтрів -------------------
class DynamicProductFilterForm(forms.Form):
    manufacturer = forms.CharField(required=False, label="Виробник")
    country = forms.CharField(required=False, label="Країна")
    min_price = forms.DecimalField(required=False, decimal_places=2, max_digits=10, label="Мін. ціна")
    max_price = forms.DecimalField(required=False, decimal_places=2, max_digits=10, label="Макс. ціна")
    available = forms.BooleanField(required=False, label="В наявності")

    def __init__(self, category=None, subcategory=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Беремо всі атрибути товарів у вибраній категорії або підкатегорії
        if subcategory:
            product_attrs = ProductAttribute.objects.filter(product__subcategory=subcategory)
        elif category:
            product_attrs = ProductAttribute.objects.filter(product__category=category)
        else:
            product_attrs = ProductAttribute.objects.none()

        # Отримуємо унікальні атрибути по назві фільтра
        unique_attrs = product_attrs.values_list('filter_option__name', flat=True).distinct()

        # Додаємо динамічні поля для цих атрибутів
        for attr_name in unique_attrs:
            field_name = f"attr_{attr_name.replace(' ', '_').lower()}"
            self.fields[field_name] = forms.CharField(
                required=False,
                label=attr_name,
                widget=forms.TextInput(attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00a046]",
                    "placeholder": f"Введіть {attr_name.lower()}"
                })
            )


# ------------------- Форма для додавання нового товару -------------------
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'subcategory', 'manufacturer', 'country', 'price', 'available', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'subcategory': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'manufacturer': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'country': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-full'}),
        }


# ------------------- Форма для атрибутів товару -------------------
class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ['filter_option', 'value']
        widgets = {
            'filter_option': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'value': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
        }


# InlineFormSet для атрибутів товару
ProductAttributeFormSet = inlineformset_factory(
    Product,
    ProductAttribute,
    form=ProductAttributeForm,
    extra=1,
    can_delete=True
)
