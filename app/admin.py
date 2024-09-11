from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from app.models import User, Category, Product, ProductImage, Brand, CartItem, OrderItems

# Register your models here.

@admin.register(User)
class UserAdmin(UserAdmin):
    model = User
    list_display = ['id', 'email', 'username', 'mobile_number', 'first_name', 'last_name', 'stripe_customer_id', 'stripe_subscription_id', 'is_subscrib' ]
    ordering = ['pk']

@admin.register(Category)
class category(admin.ModelAdmin):
    model = Category
    list_display = ['id', 'category_name', 'isDeleted']
    ordering = ['pk']


@admin.register(Product)
class product(admin.ModelAdmin):
    model = Product
    list_display = ['id', 'user', 'productName', 'description', 'rate', 'category', 'brand']
    ordering = ['pk']    

@admin.register(ProductImage)
class productImage(admin.ModelAdmin):
    model = ProductImage
    list_display = ['id', 'product', 'image_file']
    ordering = ['pk']


@admin.register(Brand)
class brand(admin.ModelAdmin):
    model = Brand
    list_display = ['id', 'brand_name', 'isDeleted']
    ordering = ['pk']


@admin.register(CartItem)
class cartItem(admin.ModelAdmin):
    model = CartItem
    list_display = ['id', 'user', 'product', 'quantity', 'image_url']
    ordering = ['pk']

@admin.register(OrderItems)
class  orderItems(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity', 'image_url']
    ordering = ['pk']

