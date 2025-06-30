from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
     path('sign-in/', views.sign_in_view, name='signIn'),
]
