from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

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

class LoginForm(forms.Form):
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