from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate
from .models import User


class UserLoginForm(AuthenticationForm):
    """
    User login form
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
            'placeholder': 'Password'
        })
    )


class UserRegistrationForm(UserCreationForm):
    """
    User registration form
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
            'placeholder': 'Email'
        })
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
            'placeholder': 'Phone Number'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500',
            'placeholder': 'Confirm Password'
        })
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
    
    def clean_email(self):
        """
        Check if email already exists
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered')
        return email