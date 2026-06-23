from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend  # 👈 YEH IMPORT
from django.db.models import Sum
from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    """
    Transaction API (CRUD)
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['transaction_id', 'order__order_number']
    filterset_fields = ['status', 'payment_method']
    ordering_fields = ['created_at', 'amount']
    
    def get_queryset(self):
        """
        Filter transactions based on user role
        """
        user = self.request.user
        if user.is_staff or user.is_restaurant_owner:
            return Transaction.objects.all()
        return Transaction.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get transaction statistics
        """
        total_transactions = Transaction.objects.count()
        total_revenue = Transaction.objects.filter(
            status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            'total_transactions': total_transactions,
            'total_revenue': total_revenue,
            'pending': Transaction.objects.filter(status='pending').count(),
            'paid': Transaction.objects.filter(status='paid').count(),
            'refunded': Transaction.objects.filter(status='refunded').count(),
            'failed': Transaction.objects.filter(status='failed').count()
        })