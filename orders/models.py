from django.db import models
from accounts.models import User
from menu.models import MenuItem


class Order(models.Model):
    """
    Order model for customer orders
    """
    # Order Status Choices
    PENDING = 'pending'
    PREPARING = 'preparing'
    ON_DELIVERY = 'on_delivery'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PREPARING, 'Preparing'),
        (ON_DELIVERY, 'On Delivery'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    # Order Type Choices
    DINE_IN = 'dine_in'
    TAKEAWAY = 'takeaway'
    DELIVERY = 'delivery'
    
    TYPE_CHOICES = [
        (DINE_IN, 'Dine-In'),
        (TAKEAWAY, 'Takeaway'),
        (DELIVERY, 'Delivery'),
    ]
    
    # Payment Status Choices
    PAYMENT_PENDING = 'pending'
    PAID = 'paid'
    REFUNDED = 'refunded'
    FAILED = 'failed'
    
    PAYMENT_CHOICES = [
        (PAYMENT_PENDING, 'Pending'),
        (PAID, 'Paid'),
        (REFUNDED, 'Refunded'),
        (FAILED, 'Failed'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    customer_email = models.EmailField(blank=True)
    customer_address = models.TextField(blank=True)
    
    order_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=DINE_IN)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=PAYMENT_PENDING)
    payment_method = models.CharField(max_length=50, blank=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    table_number = models.IntegerField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    """
    Order items model
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"
    
    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)