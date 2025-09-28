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
    path('profile/avatar/', views.update_avatar, name='profile_update_avatar'),
    path('review/add/<int:product_id>/', views.review_form, name='add_review'),
    path('review/edit/<int:review_id>/', views.review_form, name='edit_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
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
        # Cart AJAX endpoints
    path('cart/add/', views.cart_add_ajax, name='cart_add_ajax'),
    path('cart/remove/', views.cart_remove_ajax, name='cart_remove_ajax'),
    path('cart/update/', views.cart_update_quantity_ajax, name='cart_update_quantity_ajax'),
    path('cart/get/', views.cart_get_ajax, name='cart_get_ajax'),
    path('cart/promo/', views.cart_apply_promo_ajax, name='cart_apply_promo_ajax'),
    path('payment/', views.payment_page, name='payment_page'),
        # Order processing
    path('process-payment/', views.process_payment, name='process_payment'),
    path('order-success/<str:order_number>/', views.order_success, name='order_success'),
    path('order-history/', views.order_history, name='order_history'),
    path('order/<str:order_number>/', views.order_detail, name='order_detail'),
        # Favorites AJAX endpoint
    path('favorites/json/', views.favorites_list, name='favorites_list'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path("cart/update/<int:product_id>/", views.cart_update_quantity, name="cart_update_quantity"),



]
