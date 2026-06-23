from django.contrib import admin
from .models import Category, MenuItem, MenuItemImage


class MenuItemImageInline(admin.TabularInline):
    model = MenuItemImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'is_featured', 'rating')
    list_filter = ('category', 'is_available', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [MenuItemImageInline]