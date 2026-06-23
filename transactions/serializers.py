from rest_framework import serializers
from .models import Transaction
from orders.serializers import OrderSerializer


class TransactionSerializer(serializers.ModelSerializer):
    """
    Transaction serializer
    """
    order_details = OrderSerializer(source='order', read_only=True)
    user_name = serializers.ReadOnlyField(source='user.username', default='Guest')
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_id', 'order', 'order_details', 
            'user', 'user_name', 'amount', 'payment_method', 
            'status', 'response_data', 'created_at'
        ]
        read_only_fields = ['transaction_id', 'created_at']