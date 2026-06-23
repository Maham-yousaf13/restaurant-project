from django.urls import path
from .views import book_table, booking_success

urlpatterns = [
    path('', book_table, name='book_table'),
    path('success/', booking_success, name='booking_success'),
]