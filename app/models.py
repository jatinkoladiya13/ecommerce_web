from django.db import models
from django.contrib.auth.models  import AbstractUser
import os

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True,  blank=True)
    mobile_number = models.IntegerField(default=0, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    is_subscrib = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    def __str__(self) -> str:
        return f'{self.username}'
    

class Category(models.Model):
    category_name = models.CharField(max_length=255, null=True, blank=True)    
    isDeleted = models.BooleanField(blank=True, null=True)

    def __str__(self):
            return self.category_name
    
class Brand(models.Model):
    brand_name = models.CharField(max_length=255, null=True, blank=True)    
    isDeleted = models.BooleanField(blank=True, null=True)


    def __str__(self):
            return self.brand_name

class Product(models.Model):
    user = models.ForeignKey(User,  on_delete=models.CASCADE)
    productName = models.CharField(max_length=255)
    description = models.TextField()
    rate = models.DecimalField(max_digits=10, decimal_places=2) 
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.productName
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_file = models.ImageField(upload_to='product_images/')  

    def delete(self,  *args, **kwargs): 
        if self.image_file:
            if os.path.isfile(self.image_file.path):
                 os.remove(self.image_file.path) 
        super().delete(*args, **kwargs)         
             


class CartItem(models.Model):
    user = models.ForeignKey(User,  on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    image_url = models.CharField(max_length=255, null=True, blank=True) 

class OrderItems(models.Model):
    user = models.ForeignKey(User,  on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    image_url = models.CharField(max_length=255, null=True, blank=True)     