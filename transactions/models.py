from django.db import models
from accounts.models import User
from orders.models import Order


class Transaction(models.Model):
    """
    Transaction model for payment records
    """
    transaction_id = models.CharField(max_length=100, unique=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20)  # paid, pending, refunded, failed
    response_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"TXN #{self.transaction_id}"
    
    class Meta:
        ordering = ['-created_at']