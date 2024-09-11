from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.homepage, name='home'),
    path('shop/',views.shoppage),
    path('search/',views.search_items),
    path('blog/', views.blogpage),
    path('about/', views.aboutpage),
    path('contact/',views.contactpage),
    path('wishlist/',views.wishlistpage),
    path('cart/',views.cartpage, name='cart'),
    path('update_quantity_cart/',views.update_quantity_cart, name='update_quantity_cart'),
    path('remove_from_cart/',views.remove_from_cart, name='remove_from_cart'),
    path('cart/<int:product_id>',views.cartpage, name='add-cart'),
    path('pay_order/', views.pay_order, name='pay_order'),
    path('success_payment/', views.success_payment, name='success_payment'),
    path('orders/', views.orders, name='orders'),
    path('sproduct/<int:product_id>/',views.sproductpage, name='sproduct'),
    path('userprofile/',views.userprofile, name='userprofile'),
    path('login/',views.loginpage, name='login'),
    path('signout/', views.signout),
    path('signup/', views.register),
    path('sendlink/', views.sendlink, name='sendlink'),
    path('resetpassword/<uid>/<token>/', views.resetpassword),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('category/', views.category, name='category'),
    path('category_view/', views.category_view, name='category_view'),
    path('category_delete/', views.category_delete, name='category_delete'),
    path('category_update/', views.category_update, name='category_update'),
    path('brand/', views.brand, name='brand'),
    path('brand_view/', views.brand_view, name='brand_view'),
    path('brand_delete/', views.brand_delete, name='brand_delete'),
    path('brand_update/', views.brand_update, name='brand_update'),
    path('productadd/', views.product_add, name='productadd'),
    path('product_view/', views.product_view, name='product_view'),
    path('product_delete/', views.product_delete, name='product_delete'),
    path('product_update/<str:encrypted_id>/', views.product_update, name='product_update'),
    path('network_error/', views.network_error, name="network_error"),
    path('checkout_session/<int:user_id>',views.checkout_session,name='checkout_session'),
    path('pay_success',views.pay_success,name='pay_success'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('checkout_subscription/<int:amount>/', views.checkout_subscription, name='checkout_subscription'),
    path('subscription_pay_succcess/',views.subscription_pay_succcess,name='subscription_pay_succcess'),
    path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('update_subscription/<int:amount>/', views.update_subscription, name='update_subscription'),
    path('cancel_subscription/', views.cancel_subscription, name='cancel_subscription'),
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)