from django.urls import path
from .views import register, login, custom_login, google_login

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('social-login/', custom_login, name='social_login'),
    path('google/', google_login, name='google_login'),  
]
