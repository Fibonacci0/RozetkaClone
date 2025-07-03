from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('profile/', views.user_profile, name='user_profile'),
    path('reviews/create/', views.create_review, name='create_review'),
    path('reviews/', views.reviews_list, name='reviews_list'),
]
