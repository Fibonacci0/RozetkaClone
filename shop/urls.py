from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('register_email/', views.register_email, name='register_email'),
    path('register_phone_request/', views.register_phone_request, name='register_phone_request'), #
    path('login/', views.user_login, name='login'),
    path('login_email/', views.login_email, name='login_email'),
    path('login_phone_request/', views.login_phone_request, name='login_phone_request'), #
    path('verify_phone_code/', views.verify_phone_code, name='verify_phone_code'), #
    path('resend_sms/',views.resend_sms, name='resend_sms'), #
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('all_categories/', views.all_categories, name='all_categories'),
    path('search/', views.search_products, name='search_products'),
    path('product/<int:product_id>/review/create/', views.review_form, name='create_review'),
    path('review/<int:review_id>/edit', views.review_form, name='edit_review'),
    path('review/<int:review_id>/delete', views.delete_review, name='delete_review'),
    path('category/<slug:category_slug>/', views.home, name='home'),

    path("password-reset/", views.password_reset_request, name="password_reset"),
    path("reset/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),

]
