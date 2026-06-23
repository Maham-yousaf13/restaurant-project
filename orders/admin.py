from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'status', 'total', 'order_type', 'created_at')
    list_filter = ('status', 'order_type', 'payment_status')
    search_fields = ('order_number', 'customer_name', 'customer_phone')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at')