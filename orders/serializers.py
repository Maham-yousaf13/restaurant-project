from rest_framework import serializers
from .models import Order, OrderItem
from menu.serializers import MenuItemSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Order item serializer
    """
    menu_item_details = MenuItemSerializer(source='menu_item', read_only=True)
    item_name = serializers.ReadOnlyField(source='menu_item.name')
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'menu_item', 'menu_item_details', 'item_name',
            'quantity', 'price', 'total', 'special_instructions'
        ]


class OrderSerializer(serializers.ModelSerializer):
    """
    Order serializer
    """
    items = OrderItemSerializer(many=True, source='orderitem_set', read_only=True)
    user_name = serializers.ReadOnlyField(source='user.username', default='Guest')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    order_type_display = serializers.ReadOnlyField(source='get_order_type_display')
    payment_status_display = serializers.ReadOnlyField(source='get_payment_status_display')
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'user_name', 'customer_name', 
            'customer_phone', 'customer_email', 'customer_address',
            'order_type', 'order_type_display', 'status', 'status_display',
            'payment_status', 'payment_status_display', 'payment_method',
            'subtotal', 'tax', 'delivery_charge', 'discount', 'total',
            'notes', 'table_number', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """
        Create order with items
        """
        items_data = validated_data.pop('orderitem_set', [])
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        # Calculate total
        order.subtotal = sum(item.total for item in order.items.all())
        order.tax = order.subtotal * 0.10  # 10% tax
        order.total = order.subtotal + order.tax + order.delivery_charge - order.discount
        order.save()
        
        return order


class OrderStatsSerializer(serializers.Serializer):
    """
    Order statistics serializer
    """
    total = serializers.IntegerField()
    pending = serializers.IntegerField()
    preparing = serializers.IntegerField()
    on_delivery = serializers.IntegerField()
    completed = serializers.IntegerField()
    cancelled = serializers.IntegerField()