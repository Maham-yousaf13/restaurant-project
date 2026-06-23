from rest_framework import serializers
from .models import Category, MenuItem, MenuItemImage


class CategorySerializer(serializers.ModelSerializer):
    """
    Category serializer
    """
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'is_active', 'item_count', 'created_at']
    
    def get_item_count(self, obj):
        return obj.items.filter(is_available=True).count()


class MenuItemImageSerializer(serializers.ModelSerializer):
    """
    Menu item image serializer
    """
    class Meta:
        model = MenuItemImage
        fields = ['id', 'image', 'is_primary']


class MenuItemSerializer(serializers.ModelSerializer):
    """
    Menu item serializer
    """
    category_name = serializers.ReadOnlyField(source='category.name')
    category_slug = serializers.ReadOnlyField(source='category.slug')
    extra_images = MenuItemImageSerializer(many=True, read_only=True)
    final_price = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'discount_price', 
            'final_price', 'category', 'category_name', 'category_slug',
            'image', 'extra_images', 'is_available', 'is_featured', 
            'rating', 'preparation_time', 'ingredients', 'calories',
            'created_at', 'updated_at'
        ]
    
    def get_final_price(self, obj):
        """
        Return discounted price if available, else return original price
        """
        if obj.discount_price and obj.discount_price < obj.price:
            return obj.discount_price
        return obj.price