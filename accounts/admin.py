from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin panel for User model
    """
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_restaurant_owner', 'created_at')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('is_staff', 'is_restaurant_owner', 'is_active')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('phone', 'address', 'profile_picture', 'is_restaurant_owner')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extra Info', {'fields': ('phone', 'address', 'profile_picture', 'is_restaurant_owner')}),
    )