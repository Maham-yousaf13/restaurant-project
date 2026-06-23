from django.db import models


class Category(models.Model):
    """
    Category model for menu items
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']


class MenuItem(models.Model):
    """
    Menu item model
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    image = models.ImageField(upload_to='menu/')
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    rating = models.FloatField(default=4.0)
    preparation_time = models.IntegerField(default=15, help_text="Minutes")
    ingredients = models.TextField(blank=True)
    calories = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class MenuItemImage(models.Model):
    """
    Extra images for menu items
    """
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='extra_images')
    image = models.ImageField(upload_to='menu/extra/')
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.menu_item.name} - Extra Image"