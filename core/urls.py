from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from feedback.views import feedback_list
from blog.views import admin_blog_posts, admin_blog_create, admin_blog_edit, admin_blog_delete
# Import views
from .views import home, dashboard, order_history, profile
from menu.views import (
    CategoryViewSet, MenuItemViewSet, menu_list, menu_detail,
    add_to_cart, view_cart, update_cart, clear_cart, checkout, order_confirmation,
    create_payment_intent, payment_page, payment_success, payment_cancel, stripe_webhook
)
from orders.views import OrderViewSet, admin_orders, admin_order_detail
from blog.views import BlogCategoryViewSet, BlogPostViewSet, BlogCommentViewSet, blog_list, blog_detail
from transactions.views import TransactionViewSet
from accounts.views import login_view, register_view, logout_view

# Create router for API endpoints
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'menu', MenuItemViewSet, basename='menu')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'blog-categories', BlogCategoryViewSet, basename='blog-category')
router.register(r'blog', BlogPostViewSet, basename='blog')
router.register(r'blog-comments', BlogCommentViewSet, basename='blog-comment')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    
    # Frontend URLs
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('orders/history/', order_history, name='order_history'),
    path('profile/', profile, name='profile'),
    
    # Add this URL in urlpatterns
path('feedback/', include('feedback.urls')),

    # Menu URLs
    path('menu/', menu_list, name='menu_list'),
    path('menu/<slug:slug>/', menu_detail, name='menu_detail'),
    
    path('blog-admin/', admin_blog_posts, name='admin_blog_posts'),
path('blog-admin/create/', admin_blog_create, name='admin_blog_create'),
path('blog-admin/edit/<int:post_id>/', admin_blog_edit, name='admin_blog_edit'),
path('blog-admin/delete/<int:post_id>/', admin_blog_delete, name='admin_blog_delete'),
    # Cart URLs
    path('cart/add/<int:item_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/update/', update_cart, name='update_cart'),
    path('cart/clear/', clear_cart, name='clear_cart'),
    path('checkout/', checkout, name='checkout'),
    path('order/confirmation/<int:order_id>/', order_confirmation, name='order_confirmation'),
    
    # Payment URLs
    path('create-payment-intent/<int:order_id>/', create_payment_intent, name='create_payment_intent'),
    path('payment/<int:order_id>/', payment_page, name='payment_page'),
    path('payment-success/<int:order_id>/', payment_success, name='payment_success'),
    path('payment-cancel/<int:order_id>/', payment_cancel, name='payment_cancel'),
    path('webhook/stripe/', stripe_webhook, name='stripe_webhook'),
    
    # Blog URLs
    path('blog/', blog_list, name='blog_list'),
    path('blog/<slug:slug>/', blog_detail, name='blog_detail'),
    
    # Book a Table URLs
    path('book/', include('reservations.urls')),
    
    # Admin Order Management URLs
    path('admin-orders/', admin_orders, name='admin_orders'),
    path('admin-orders/<int:order_id>/', admin_order_detail, name='admin_order_detail'),
    
    # Auth URLs
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    
    # API URLs
    path('api/', include(router.urls)),
    path('api/auth/', include('accounts.urls')),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)