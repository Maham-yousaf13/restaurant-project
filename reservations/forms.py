from django import forms
from .models import Reservation
from datetime import datetime

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['name', 'email', 'phone', 'date', 'time', 'guests', 'table_number', 'special_requests']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
                'min': datetime.now().date().isoformat()
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500'
            }),
            'guests': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
                'min': 1,
                'max': 20
            }),
            'table_number': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500'
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
                'rows': 3,
                'placeholder': 'Any special requests?'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        table_number = cleaned_data.get('table_number')
        
        if date and time and table_number:
            # Check if table is already booked
            if Reservation.objects.filter(
                date=date,
                time=time,
                table_number=table_number,
                status__in=['pending', 'confirmed']
            ).exists():
                raise forms.ValidationError(
                    f'Table {table_number} is already booked for {date} at {time}. Please select another time or table.'
                )
        return cleaned_data