from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer
from orders.models import Order, OrderItem
import json
import random
import stripe


# ==================== STRIPE CONFIGURATION ====================
stripe.api_key = settings.STRIPE_SECRET_KEY


# ==================== API VIEWS ====================

class CategoryViewSet(viewsets.ModelViewSet):
    """
    Category API (CRUD operations)
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    
    @action(detail=False, methods=['get'])
    def all_with_items(self, request):
        """
        Get all categories with their items
        """
        categories = self.get_queryset().prefetch_related('items')
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class MenuItemViewSet(viewsets.ModelViewSet):
    """
    Menu Item API (CRUD operations)
    """
    queryset = MenuItem.objects.filter(is_available=True)
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'name', 'rating', 'created_at']
    filterset_fields = ['category', 'is_available', 'is_featured']
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured menu items
        """
        featured_items = MenuItem.objects.filter(
            is_featured=True, 
            is_available=True
        )
        serializer = self.get_serializer(featured_items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get menu items by category slug
        """
        category_slug = request.query_params.get('category')
        if not category_slug:
            return Response(
                {'error': 'Category slug required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            category = Category.objects.get(slug=category_slug)
            items = MenuItem.objects.filter(
                category=category, 
                is_available=True
            )
            serializer = self.get_serializer(items, many=True)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response(
                {'error': 'Category not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Advanced search for menu items
        """
        query = request.query_params.get('q', '')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        category = request.query_params.get('category')
        
        queryset = self.get_queryset()
        
        if query:
            queryset = queryset.filter(
                models.Q(name__icontains=query) |
                models.Q(description__icontains=query)
            )
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        if category:
            queryset = queryset.filter(category__slug=category)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ==================== FRONTEND VIEWS ====================

def menu_list(request):
    """
    Display all menu items with categories
    """
    categories = Category.objects.filter(is_active=True)
    menu_items = MenuItem.objects.filter(is_available=True)
    
    # Get category filter from URL
    category_slug = request.GET.get('category')
    if category_slug:
        menu_items = menu_items.filter(category__slug=category_slug)
    
    context = {
        'categories': categories,
        'menu_items': menu_items,
        'active_category': category_slug,
    }
    return render(request, 'menu/list.html', context)


def menu_detail(request, slug):
    """
    Display single menu item detail
    """
    menu_item = get_object_or_404(MenuItem, slug=slug, is_available=True)
    context = {
        'item': menu_item,
    }
    return render(request, 'menu/detail.html', context)


def add_to_cart(request, item_id):
    """
    Add item to cart using session
    """
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        # Get or create cart in session
        cart = request.session.get('cart', {})
        
        # Add item to cart
        if str(item_id) in cart:
            cart[str(item_id)]['quantity'] += quantity
        else:
            # Get item from database
            try:
                item = MenuItem.objects.get(id=item_id, is_available=True)
                cart[str(item_id)] = {
                    'id': item.id,
                    'name': item.name,
                    'price': str(item.price),
                    'quantity': quantity,
                    'image': item.image.url if item.image else '',
                }
            except MenuItem.DoesNotExist:
                return JsonResponse({'error': 'Item not found'}, status=404)
        
        # Save cart to session
        request.session['cart'] = cart
        request.session.modified = True
        
        # Return response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{item.name} added to cart!',
                'cart_count': sum(item['quantity'] for item in cart.values())
            })
        else:
            messages.success(request, f'{item.name} added to cart!')
            return redirect('view_cart')
    
    return redirect('menu_list')


def view_cart(request):
    """
    View cart page with calculated totals
    """
    cart = request.session.get('cart', {})
    cart_items = list(cart.values())
    
    # Calculate totals
    subtotal = 0
    for item in cart_items:
        item_total = float(item['price']) * item['quantity']
        subtotal += item_total
    
    tax = subtotal * 0.10
    delivery_charge = 5.00
    grand_total = subtotal + tax + delivery_charge
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'delivery_charge': delivery_charge,
        'grand_total': grand_total,
        'cart_count': sum(item['quantity'] for item in cart_items),
    }
    return render(request, 'orders/cart.html', context)


def update_cart(request):
    """
    Update cart item quantity (increase, decrease, remove)
    """
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')
        
        cart = request.session.get('cart', {})
        
        if str(item_id) in cart:
            if action == 'increase':
                cart[str(item_id)]['quantity'] += 1
            elif action == 'decrease':
                cart[str(item_id)]['quantity'] -= 1
                if cart[str(item_id)]['quantity'] <= 0:
                    del cart[str(item_id)]
            elif action == 'remove':
                del cart[str(item_id)]
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'cart_count': sum(item['quantity'] for item in cart.values())
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def clear_cart(request):
    """
    Clear all items from cart
    """
    request.session['cart'] = {}
    request.session.modified = True
    messages.success(request, 'Cart cleared successfully!')
    return redirect('view_cart')


def checkout(request):
    """
    Checkout page - Place order
    """
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('menu_list')
    
    cart_items = list(cart.values())
    
    # Calculate totals
    subtotal = 0
    for item in cart_items:
        item_total = float(item['price']) * item['quantity']
        subtotal += item_total
    
    tax = subtotal * 0.10
    delivery_charge = 5.00
    grand_total = subtotal + tax + delivery_charge
    
    if request.method == 'POST':
        # Get form data
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        customer_email = request.POST.get('customer_email')
        customer_address = request.POST.get('customer_address', '')
        order_type = request.POST.get('order_type', 'dine_in')
        notes = request.POST.get('notes', '')
        
        # Generate unique order number
        def generate_order_number():
            while True:
                number = str(random.randint(1000, 9999))
                if not Order.objects.filter(order_number=number).exists():
                    return number
        
        order_number = generate_order_number()
        
        # Create order
        order = Order.objects.create(
            order_number=order_number,
            user=request.user if request.user.is_authenticated else None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            customer_address=customer_address,
            order_type=order_type,
            subtotal=subtotal,
            tax=tax,
            delivery_charge=delivery_charge if order_type == 'delivery' else 0,
            total=grand_total if order_type == 'delivery' else subtotal + tax,
            notes=notes,
            status='pending',
            payment_status='pending',
        )
        
        # Create order items
        for item in cart_items:
            menu_item = MenuItem.objects.get(id=item['id'])
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=item['quantity'],
                price=float(item['price']),
                total=float(item['price']) * item['quantity']
            )
        
        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True
        
        messages.success(request, f'Order #{order.order_number} placed successfully!')
        return redirect('order_confirmation', order_id=order.id)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'delivery_charge': delivery_charge,
        'grand_total': grand_total,
    }
    return render(request, 'orders/checkout.html', context)


def order_confirmation(request, order_id):
    """
    Order confirmation page
    """
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'orders/confirmation.html', context)


# ==================== PAYMENT VIEWS ====================

def create_payment_intent(request, order_id):
    """
    Create Stripe payment intent for order
    """
    order = get_object_or_404(Order, id=order_id)
    
    try:
        # Create PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(order.total * 100),  # Convert dollars to cents
            currency='usd',
            metadata={
                'order_id': order.id,
                'order_number': order.order_number,
            },
        )
        
        return JsonResponse({
            'client_secret': intent.client_secret,
            'order_id': order.id,
        })
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def payment_page(request, order_id):
    """
    Payment page
    """
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'orders/payment.html', context)


def payment_success(request, order_id):
    """
    Payment success page
    """
    order = get_object_or_404(Order, id=order_id)
    order.payment_status = 'paid'
    order.status = 'preparing'
    order.save()
    
    context = {
        'order': order,
    }
    return render(request, 'orders/payment_success.html', context)


def payment_cancel(request, order_id):
    """
    Payment cancelled page
    """
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'orders/payment_cancel.html', context)


# ==================== STRIPE WEBHOOK ====================

@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhook endpoint - Handles payment events
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Update order status
        order_id = payment_intent.get('metadata', {}).get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.payment_status = 'paid'
                order.status = 'preparing'
                order.save()
            except Order.DoesNotExist:
                pass
    
    return HttpResponse(status=200)