from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'time', 'guests', 'status', 'phone')
    list_filter = ('status', 'date')
    search_fields = ('name', 'email', 'phone')