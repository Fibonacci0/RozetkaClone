from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Review
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
User = get_user_model()

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
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'example@email.com'
        })
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'Пароль'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            from django.contrib.auth import authenticate
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Невірний email або пароль")
            cleaned_data['user'] = user
        return cleaned_data

class EmailRegisterForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'example@email.com'
        })
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'Пароль'
        })
    )
    password2 = forms.CharField(
        label="Підтвердження пароля",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'Повторіть пароль'
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Користувач з таким email вже існує")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError("Паролі не співпадають")
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
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 text-gray-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'value': '+38 ',
        })
    )

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
    email = forms.EmailField(
        label="Пошта",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            'placeholder': 'example@email.com'
        })
    )

class PasswordResetConfirmForm(forms.Form):
    password = forms.CharField(
        label="Новий пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            "placeholder": "Введіть новий пароль"
        })
    )
    password2 = forms.CharField(
        label="Повторіть пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400',
            "placeholder": "Повторіть пароль"
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Паролі не співпадають")
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
