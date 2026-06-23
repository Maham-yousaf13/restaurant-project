from django.urls import path
from .views import (
    blog_list, blog_detail,
    admin_blog_posts, admin_blog_create, admin_blog_edit, admin_blog_delete
)

urlpatterns = [
    # Public URLs
    path('', blog_list, name='blog_list'),
    path('<slug:slug>/', blog_detail, name='blog_detail'),
    
    # Admin URLs
    path('admin/', admin_blog_posts, name='admin_blog_posts'),
    path('admin/create/', admin_blog_create, name='admin_blog_create'),
    path('admin/edit/<int:post_id>/', admin_blog_edit, name='admin_blog_edit'),
    path('admin/delete/<int:post_id>/', admin_blog_delete, name='admin_blog_delete'),
]