from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('auth/', include('authorization.urls')),
    path('accounts/', include('allauth.urls')),
]


