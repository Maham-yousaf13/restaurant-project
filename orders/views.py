from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderStatsSerializer
from menu.models import MenuItem
import random


# ==================== API VIEWS ====================

class OrderViewSet(viewsets.ModelViewSet):
    """
    Order API (CRUD operations)
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['order_number', 'customer_name', 'customer_phone']
    filterset_fields = ['status', 'order_type', 'payment_status']
    ordering_fields = ['created_at', 'total']
    
    def get_queryset(self):
        """
        Filter orders based on user role
        """
        user = self.request.user
        if user.is_restaurant_owner or user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """
        Generate order number and create order
        """
        order_number = self.generate_order_number()
        serializer.save(
            user=self.request.user,
            order_number=order_number
        )
    
    def generate_order_number(self):
        """
        Generate unique 4-digit order number
        """
        while True:
            number = str(random.randint(1000, 9999))
            if not Order.objects.filter(order_number=number).exists():
                return number
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update order status
        """
        order = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'Status required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            return Response({
                'message': 'Status updated',
                'status': order.status,
                'status_display': order.get_status_display()
            })
        
        return Response(
            {'error': 'Invalid status'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['patch'])
    def update_payment_status(self, request, pk=None):
        """
        Update payment status
        """
        order = self.get_object()
        payment_status = request.data.get('payment_status')
        
        if not payment_status:
            return Response(
                {'error': 'Payment status required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if payment_status in dict(Order.PAYMENT_CHOICES):
            order.payment_status = payment_status
            order.save()
            return Response({
                'message': 'Payment status updated',
                'payment_status': order.payment_status,
                'payment_status_display': order.get_payment_status_display()
            })
        
        return Response(
            {'error': 'Invalid payment status'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get order statistics
        """
        stats_data = {
            'total': Order.objects.count(),
            'pending': Order.objects.filter(status='pending').count(),
            'preparing': Order.objects.filter(status='preparing').count(),
            'on_delivery': Order.objects.filter(status='on_delivery').count(),
            'completed': Order.objects.filter(status='completed').count(),
            'cancelled': Order.objects.filter(status='cancelled').count()
        }
        serializer = OrderStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def revenue(self, request):
        """
        Get revenue statistics
        """
        total_revenue = Order.objects.filter(
            status='completed'
        ).aggregate(
            total=Sum('total')
        )['total'] or 0
        
        total_orders = Order.objects.filter(status='completed').count()
        
        return Response({
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'average_order_value': total_revenue / total_orders if total_orders > 0 else 0
        })
    
    @action(detail=False, methods=['get'])
    def today_stats(self, request):
        """
        Get today's order statistics
        """
        today = timezone.now().date()
        
        today_orders = Order.objects.filter(created_at__date=today)
        
        return Response({
            'today_orders': today_orders.count(),
            'today_revenue': today_orders.filter(status='completed').aggregate(
                total=Sum('total')
            )['total'] or 0,
            'today_pending': today_orders.filter(status='pending').count(),
            'today_completed': today_orders.filter(status='completed').count()
        })


# ==================== FRONTEND ADMIN VIEWS ====================

@login_required
def admin_orders(request):
    """
    Admin orders management page
    """
    # Check if user is admin or restaurant owner
    if not (request.user.is_staff or request.user.is_restaurant_owner):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    # Get all orders
    orders = Order.objects.all().order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter and status_filter in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status_filter)
    
    # Search by order number or customer name
    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(customer_phone__icontains=search_query)
        )
    
    # Get status counts for the filter buttons
    status_counts = {
        'all': Order.objects.count(),
        'pending': Order.objects.filter(status='pending').count(),
        'preparing': Order.objects.filter(status='preparing').count(),
        'on_delivery': Order.objects.filter(status='on_delivery').count(),
        'completed': Order.objects.filter(status='completed').count(),
        'cancelled': Order.objects.filter(status='cancelled').count(),
    }
    
    context = {
        'orders': orders,
        'status_counts': status_counts,
        'current_status': status_filter,
        'search_query': search_query,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'orders/admin_orders.html', context)


@login_required
def admin_order_detail(request, order_id):
    """
    Admin order detail page
    """
    # Check if user is admin or restaurant owner
    if not (request.user.is_staff or request.user.is_restaurant_owner):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.order_number} status updated to {order.get_status_display()}')
            return redirect('admin_order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'orders/admin_order_detail.html', context)