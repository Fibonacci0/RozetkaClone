from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Review
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model, password_validation
from django.utils.safestring import mark_safe
from django.core.validators import RegexValidator, EmailValidator
import re

User = get_user_model()


class UserProfileForm(forms.ModelForm):
    username = forms.CharField(
        label='Username',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full mt-1 px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'Ваш Username'
        })
    )

    first_name = forms.CharField(
        label='Ім\'я',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full mt-1 px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'Ваше ім\'я'
        })
    )

    last_name = forms.CharField(
        label='Прізвище',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full mt-1 px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'Ваше прізвище'
        })
    )

    email = forms.CharField(
        label='Пошта',
        max_length=30,
        required=False,
        validators=[EmailValidator(message="Введіть правильний email (наприклад, example@mail.com)")],
        widget=forms.EmailInput(attrs={
            'class': 'w-full mt-1 px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'Ваша пошта ()'
        })
    )

    phone_number = forms.CharField(
        label='Номер телефону',
        max_length=30,
        required=False,
        validators=[RegexValidator(
            regex = r'^\+38\s?\d{10}$',
            message="Номер повинен бути у форматі (+38 XXXXXXXXXX)"
        )],

        widget=forms.TextInput(attrs={
            'class': 'w-full mt-1 px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'Ваш номер телефону ()'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone_number')

        if not email and not phone:
            raise forms.ValidationError(
                "Вкажіть принаймні один контакт: \"Пошта\" або \"номер телефону\""
            )
                
        for field in ['first_name', 'last_name', 'email', 'phone_number']:
            value = cleaned_data.get(field)
            if value is not None:
                value = value.strip()
            if not value:
                cleaned_data[field] = None
            else:
                cleaned_data[field] = value

        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError("Цей username вже використовується.")
        return username

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            return phone.replace(" ", "")
        return None
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip()
            if email == "":
                return None
            return email
        return None




class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label="Старий пароль",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full mt-1 px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            })
    )
    new_password1 = forms.CharField(
        label="Новий пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full mt-1 px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            }),
        help_text= None
    )
    new_password2 = forms.CharField(
        label="Повторіть новий пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full mt-1 px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            })
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        if not self.user.has_usable_password():
            self.fields.pop('old_password')


    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if self.user.has_usable_password() and not self.user.check_password(old_password):
            raise forms.ValidationError("Неправильний старий пароль.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Паролі не співпадають.")

        if password1:
            password_validation.validate_password(password1, self.user)

        return cleaned_data

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Ім’я',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00a046]',
            'placeholder': 'Ваше ім’я'
        })
    )
    last_name = forms.CharField(
        label='Прізвище',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00a046]',
            'placeholder': 'Ваше прізвище'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00a046]',
            'placeholder': 'example@email.com'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        label="Пошта",
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'example@email.com'
        })
    )
    password = forms.CharField(
        label="Пароль",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'Пароль'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if not email:
            self.add_error("email", "Введіть email")
        if not password:
            self.add_error("password", "Введіть пароль")

        if email and password:
            from django.contrib.auth import authenticate
            user = authenticate(username=email, password=password)
            if user is None:
                self.add_error("email", "Невірний email або пароль")
                self.add_error("password", "Невірний email або пароль")
            else:
                cleaned_data['user'] = user
        return cleaned_data

class EmailRegisterForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'example@email.com'
        })
    )
    password = forms.CharField(
        label="Пароль",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'Пароль'
        })
    )
    password2 = forms.CharField(
        label="Підтвердження пароля",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'Повторіть пароль'
        })
    )

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            self.add_error("email", "Введіть пошту")
            return None
        
        if User.objects.filter(email=email).exists():
            self.add_error("email", "Користувач з такою поштою вже існує")
            return None
        
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if not password:
            self.add_error("password", "Введіть пароль")
        if not password2:
            self.add_error("password2", "Повторіть пароль")
        if password and password2 and password != password2:
            self.add_error("password2", "Паролі не співпадають")

        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        return user


class PhoneLoginForm(forms.Form):
    phone = forms.CharField(
        label="Номер телефону",
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 text-gray-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'value': '+38 ',
        })
    )
    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").replace(" ", "")
        
        if not phone:
            self.add_error("phone", "Введіть номер телефону")
            return None
        
        regex = r'^\+38\d{10}$'
        if not re.match(regex, phone):
            self.add_error("phone", "Номер повинен бути у форматі (+38 XXXXXXXXXX)")
            return None
        
        if not User.objects.filter(phone_number=phone).exists():
            self.add_error("phone", "Користувача з таким номером не існує")
            return None

        return phone


class PhoneRegisterForm(forms.Form):
    phone = forms.CharField(
        label="Номер телефону",
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 text-gray-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'value': '+38 ',
        })
    )
    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").replace(" ", "")
        
        if not phone:
            self.add_error("phone", "Введіть номер телефону")
            return None
        
        regex = r'^\+38\d{10}$'
        if not re.match(regex, phone):
            self.add_error("phone", "Номер повинен бути у форматі (+38 XXXXXXXXXX)")
            return None

        return phone


class CodeInput(forms.TextInput):
    template_name = "django/forms/widgets/text.html"

    def render(self, name, value, attrs=None, renderer=None):
        hidden = f'<input type="hidden" name="{name}" value="{value or ""}" />'

        boxes = "".join([
            f'<input type="text" maxlength="1" class="w-12 h-12 text-center border-2 border-orange-400 rounded-lg mx-2 focus:outline-none" data-code-box="{i}" />'
            for i in range(6)
        ])

        script = f"""
        <script>
        document.addEventListener("DOMContentLoaded", function() {{
            const hidden = document.querySelector("input[name='{name}']");
            const boxes = document.querySelectorAll("[data-code-box]");

            function updateHidden() {{
                hidden.value = Array.from(boxes).map(b => b.value).join("");
            }}

            boxes.forEach((box, idx) => {{
                box.addEventListener("input", () => {{
                    if (box.value.length > 0 && idx < 5) {{
                        boxes[idx + 1].focus();
                    }}
                    updateHidden();
                }});

                box.addEventListener("keydown", (e) => {{
                    if (e.key === "Backspace" && !box.value && idx > 0) {{
                        boxes[idx - 1].focus();
                    }}
                }});
            }});

            boxes[0].addEventListener("paste", (e) => {{
                e.preventDefault();
                const text = (e.clipboardData || window.clipboardData).getData("text").slice(0, 6);
                [...text].forEach((ch, i) => {{
                    if (boxes[i]) boxes[i].value = ch;
                }});
                updateHidden();
            }});
        }});
        </script>
        """

        return mark_safe(f'<div class="flex justify-center">{boxes}</div>{hidden}{script}')
    

class VerifySMSForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        widget=CodeInput()
    )


class PasswordResetRequestForm(forms.Form):
    email = forms.CharField(
        label="Пошта",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'example@email.com'
        })
    )
    
    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()

        if not email:
            self.add_error("email", "Введіть email")
            return None
        
        regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(regex, email):
            self.add_error("email", "Введіть коректний email (наприклад, example@mail.com)")
            return None

        if not User.objects.filter(email=email).exists():
            self.add_error("email", "Користувача з таким email не знайдено")
            return None

        return email

class PasswordResetConfirmForm(forms.Form):
    password = forms.CharField(
        label="Новий пароль",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            "placeholder": "Введіть новий пароль"
        })
    )
    password2 = forms.CharField(
        label="Повторіть пароль",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            "placeholder": "Повторіть пароль"
        })
    )

    def clean_password(self):
        password = self.cleaned_data.get("password", "").strip()

        if not password:
            self.add_error("password", "Введіть новий пароль")
            return None
        if len(password) < 8:
            self.add_error("password", "Пароль має містити щонайменше 8 символів")
            return None
        return password

    def clean_password2(self):
        password2 = self.cleaned_data.get("password2", "").strip()
        
        if not password2:
            self.add_error("password2", "Повторіть пароль")
            return None
        return password2

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Паролі не співпадають")
        return cleaned_data

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Ім’я користувача',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 text-base border border-gray-300 rounded-md focus:ring-2 focus:ring-[#00a046] focus:outline-none bg-gray-50'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 text-base border border-gray-300 rounded-md focus:ring-2 focus:ring-[#00a046] focus:outline-none bg-gray-50'
        })
    )
    
class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500'
            })

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        exclude = ['user', 'product']
        fields = ['rating', 'comment', 'advantages', 'disadvantages']
