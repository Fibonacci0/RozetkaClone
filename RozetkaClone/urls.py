from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
]

