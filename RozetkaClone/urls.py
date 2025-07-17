from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
<<<<<<< HEAD
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('auth/', include('authorization.urls')),
    path('accounts/', include('allauth.urls')),
=======
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

>>>>>>> f53b9dfb9ef96d8fc937ad2507ab905d2319c10a
]


