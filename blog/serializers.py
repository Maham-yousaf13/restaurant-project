from rest_framework import serializers
from .models import BlogCategory, BlogPost, BlogComment
from accounts.serializers import UserSerializer


class BlogCategorySerializer(serializers.ModelSerializer):
    """
    Blog category serializer for API
    """
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug', 'post_count']
    
    def get_post_count(self, obj):
        """
        Get count of published posts in this category
        """
        return obj.posts.filter(is_published=True).count()


class BlogCommentSerializer(serializers.ModelSerializer):
    """
    Blog comment serializer for API
    """
    user_details = UserSerializer(source='user', read_only=True)
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = BlogComment
        fields = ['id', 'post', 'user', 'username', 'user_details', 'content', 'is_approved', 'created_at']
        read_only_fields = ['user', 'created_at']


class BlogPostSerializer(serializers.ModelSerializer):
    """
    Blog post serializer for API
    """
    category_name = serializers.ReadOnlyField(source='category.name')
    author_name = serializers.ReadOnlyField(source='author.username')
    author_details = UserSerializer(source='author', read_only=True)
    comments = BlogCommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 
            'category', 'category_name', 'author', 'author_name', 'author_details',
            'featured_image', 'is_published', 'is_featured', 
            'views', 'comments', 'comment_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['views', 'created_at', 'updated_at']
    
    def get_comment_count(self, obj):
        """
        Get count of approved comments
        """
        return obj.comments.filter(is_approved=True).count()