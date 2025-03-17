from django.db import models
from django.conf import settings
from cycle.models import Product
from django.contrib.auth.models import User
from django.utils import timezone



# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', null=True)


    @property
    def total_price(self):
        return self.quantity * self.product.price
    



class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    pincode = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)  # New field for phone number
    payment_method = models.CharField(max_length=20, choices=[('UPI', 'UPI'), ('Card', 'Card Payment')])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Pending'  # Set default status
    )

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} for Order {self.order.id}"
    


