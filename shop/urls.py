from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
<<<<<<< HEAD
  
=======
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('all_categories/', views.all_categories, name='all_categories'),

    
>>>>>>> f53b9dfb9ef96d8fc937ad2507ab905d2319c10a
]
