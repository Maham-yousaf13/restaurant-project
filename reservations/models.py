from django.db import models
from accounts.models import User
from datetime import date, time


class Reservation(models.Model):
    """
    Reservation model for table booking
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    TABLE_CHOICES = [
        (1, 'Table 1 - 2 Seats'),
        (2, 'Table 2 - 2 Seats'),
        (3, 'Table 3 - 4 Seats'),
        (4, 'Table 4 - 4 Seats'),
        (5, 'Table 5 - 6 Seats'),
        (6, 'Table 6 - 6 Seats'),
        (7, 'Table 7 - 8 Seats'),
        (8, 'Table 8 - 8 Seats'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    date = models.DateField()
    time = models.TimeField()
    guests = models.PositiveIntegerField()
    table_number = models.IntegerField(choices=TABLE_CHOICES, blank=True, null=True)
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Reservation for {self.name} - {self.date} {self.time}"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = [['date', 'time', 'table_number']]  # Prevent double booking