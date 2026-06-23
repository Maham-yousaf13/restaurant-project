from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('transaction_id', 'order__order_number')