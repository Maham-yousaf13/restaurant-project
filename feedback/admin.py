from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """
    Admin configuration for Feedback model
    """
    list_display = ('name', 'rating', 'is_approved', 'created_at', 'get_rating_stars_display')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('name', 'email', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['approve_feedbacks', 'unapprove_feedbacks']
    
    def get_rating_stars_display(self, obj):
        """
        Display stars in admin list
        """
        return obj.get_rating_stars()
    get_rating_stars_display.short_description = 'Rating'
    
    def approve_feedbacks(self, request, queryset):
        """
        Bulk approve feedbacks
        """
        queryset.update(is_approved=True)
    approve_feedbacks.short_description = "Approve selected feedbacks"
    
    def unapprove_feedbacks(self, request, queryset):
        """
        Bulk unapprove feedbacks
        """
        queryset.update(is_approved=False)
    unapprove_feedbacks.short_description = "Unapprove selected feedbacks"