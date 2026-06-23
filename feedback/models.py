from django.db import models
from accounts.models import User
from orders.models import Order


class Feedback(models.Model):
    """
    Customer feedback model for collecting reviews and ratings
    """
    
    # Rating choices from 1 to 5 stars
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    # User who submitted feedback (can be null if not logged in)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='feedbacks'
    )
    
    # Order associated with feedback (optional)
    order = models.ForeignKey(
        Order, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='feedbacks'
    )
    
    # Customer details
    name = models.CharField(max_length=100)
    email = models.EmailField()
    
    # Feedback details
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    
    # Admin approval status
    is_approved = models.BooleanField(
        default=False,
        help_text="Approve to show on website"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Feedback from {self.name} - {self.rating}★"
    
    def get_rating_stars(self):
        """
        Return HTML string of star ratings
        """
        return '★' * self.rating + '☆' * (5 - self.rating)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'