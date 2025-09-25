from django.urls import path
from . import views 
urlpatterns = [
    path('', views.home, name='home'),  # Головна сторінка
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('search/', views.search_products, name='search_products'),
    path('all-categories/', views.all_categories, name='all_categories'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path("profile/", views.profile_view, name="profile"),
    path("profile/password/", views.password_view, name="profile_password"),
    path("profile/other/", views.other_view, name="profile_other"),
    path('review/add/<int:product_id>/', views.review_form, name='add_review'),
    path('review/edit/<int:review_id>/', views.review_form, name='edit_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('payment/', views.payment_page, name='payment_page'),
    path('register_email/', views.register_email, name='register_email'),
    path('register_phone_request/', views.register_phone_request, name='register_phone_request'),
    path('login_email/', views.login_email, name='login_email'),
    path('login_phone_request/', views.login_phone_request, name='login_phone_request'), #
    path('verify_phone_code/', views.verify_phone_code, name='verify_phone_code'), #
    path('resend_sms/',views.resend_sms, name='resend_sms'),
    path("password-reset/", views.password_reset_request, name="password_reset"),
    path("reset/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
    path('favorite/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
    # path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_page, name='cart_page'),
    path("cart/json/", views.cart_json, name="cart_json"),
    path("cart/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
    path('favorites/json/', views.favorites_list, name='favorites_list'),


]