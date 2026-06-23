from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'address', 
            'profile_picture', 'is_restaurant_owner', 'full_name',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['date_joined', 'last_login']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Registration serializer
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'phone', 'address']
    
    def validate(self, data):
        """
        Check passwords match
        """
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return data
    
    def create(self, validated_data):
        """
        Create user
        """
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Login serializer
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """
        Authenticate user
        """
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")


class ChangePasswordSerializer(serializers.Serializer):
    """
    Change password serializer
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, data):
        """
        Check passwords match
        """
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords don't match"})
        return data