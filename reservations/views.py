from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import Reservation
from .forms import ReservationForm


def book_table(request):
    """
    Book a table view
    """
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            if request.user.is_authenticated:
                reservation.user = request.user
            
            # Auto-assign table if not selected
            if not reservation.table_number:
                # Find available table
                available_tables = get_available_tables(reservation.date, reservation.time)
                if available_tables:
                    reservation.table_number = available_tables[0]
                else:
                    messages.error(request, 'No tables available for this time slot.')
                    return render(request, 'reservations/book.html', {'form': form})
            
            reservation.save()
            
            # Send email notification
            send_reservation_email(reservation)
            
            messages.success(request, 'Table booked successfully! We will confirm your reservation shortly.')
            return redirect('booking_success')
    else:
        form = ReservationForm()
        
        # Pre-fill form if user is logged in
        if request.user.is_authenticated:
            form.fields['name'].initial = request.user.get_full_name() or request.user.username
            form.fields['email'].initial = request.user.email
            form.fields['phone'].initial = request.user.phone
    
    return render(request, 'reservations/book.html', {'form': form})


def get_available_tables(date, time):
    """
    Get available table numbers for given date and time
    """
    booked_tables = Reservation.objects.filter(
        date=date,
        time=time,
        status__in=['pending', 'confirmed']
    ).values_list('table_number', flat=True)
    
    all_tables = list(range(1, 9))  # Tables 1 to 8
    available_tables = [t for t in all_tables if t not in booked_tables]
    return available_tables


def send_reservation_email(reservation):
    """
    Send reservation confirmation email
    """
    try:
        subject = f'Table Reservation Confirmation - AMECO Restaurant'
        message = f"""
        Dear {reservation.name},
        
        Thank you for booking a table at AMECO Restaurant!
        
        Reservation Details:
        ----------------------
        Date: {reservation.date}
        Time: {reservation.time}
        Guests: {reservation.guests}
        Table: {reservation.get_table_number_display()}
        
        We look forward to serving you!
        
        Best regards,
        AMECO Restaurant Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [reservation.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Email error: {e}")


def booking_success(request):
    """
    Booking success page
    """
    return render(request, 'reservations/success.html')


@login_required
def my_reservations(request):
    """
    View user's reservations
    """
    reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'reservations': reservations,
    }
    return render(request, 'reservations/my_reservations.html')


@login_required
def cancel_reservation(request, reservation_id):
    """
    Cancel a reservation
    """
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    if reservation.status == 'pending':
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, 'Reservation cancelled successfully.')
    else:
        messages.error(request, 'Cannot cancel this reservation.')
    return redirect('my_reservations')