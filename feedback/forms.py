from django import forms
from .models import Feedback


class FeedbackForm(forms.ModelForm):
    """
    Feedback submission form
    """
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'rating', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
                'placeholder': 'your@email.com'
            }),
            'rating': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
                'rows': 5,
                'placeholder': 'Tell us about your experience...'
            }),
        }
        labels = {
            'name': 'Full Name',
            'email': 'Email Address',
            'rating': 'Rate Your Experience',
            'comment': 'Your Feedback',
        }