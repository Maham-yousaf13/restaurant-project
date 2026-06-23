from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from menu.models import MenuItem
from orders.models import Order, OrderItem  # OrderItem added here
from blog.models import BlogPost
from transactions.models import Transaction


def home(request):
    """
    Home page view
    """
    return render(request, 'home/index.html')


@login_required
def dashboard(request):
    """
    Admin dashboard view with real statistics
    """
    # Get today's date
    today = timezone.now().date()
    
    # Order statistics
    total_orders = Order.objects.count()
    today_orders = Order.objects.filter(created_at__date=today).count()
    pending_orders = Order.objects.filter(status='pending').count()
    preparing_orders = Order.objects.filter(status='preparing').count()
    completed_orders = Order.objects.filter(status='completed').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    
    # Revenue statistics
    total_revenue = Order.objects.filter(
        status='completed'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    today_revenue = Order.objects.filter(
        status='completed',
        created_at__date=today
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Average order value
    avg_order_value = 0
    if total_orders > 0:
        avg_order_value = total_revenue / total_orders
    
    # Top selling items
    top_items = OrderItem.objects.filter(
        order__status='completed'
    ).values(
        'menu_item__name'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]
    
    # Recent orders (last 5)
    recent_orders = Order.objects.all().order_by('-created_at')[:5]
    
    # Menu items count
    total_menu_items = MenuItem.objects.count()
    active_menu_items = MenuItem.objects.filter(is_available=True).count()
    
    # Blog posts count
    total_blog_posts = BlogPost.objects.count()
    published_posts = BlogPost.objects.filter(is_published=True).count()
    
    context = {
        'total_orders': total_orders,
        'today_orders': today_orders,
        'pending_orders': pending_orders,
        'preparing_orders': preparing_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'avg_order_value': avg_order_value,
        'top_items': top_items,
        'recent_orders': recent_orders,
        'total_menu_items': total_menu_items,
        'active_menu_items': active_menu_items,
        'total_blog_posts': total_blog_posts,
        'published_posts': published_posts,
    }
    
    return render(request, 'dashboard/index.html', context)


@login_required
def order_history(request):
    """
    User order history view
    """
    user = request.user
    if user.is_staff or user.is_restaurant_owner:
        orders = Order.objects.all().order_by('-created_at')
    else:
        orders = Order.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/history.html', context)


@login_required
def profile(request):
    """
    User profile view
    """
    return render(request, 'accounts/profile.html')