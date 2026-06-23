from django.db import models
from accounts.models import User


class BlogCategory(models.Model):
    """
    Blog category model - Organizes blog posts by category
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Blog Categories'


class BlogPost(models.Model):
    """
    Blog post model - Main content for the blog
    """
    # Basic information
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True, help_text="Short summary of the post")
    
    # Relationships
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='blog_posts')
    
    # Media
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    
    # Status
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Statistics
    views = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """
        Returns the URL for this blog post
        """
        from django.urls import reverse
        return reverse('blog_detail', kwargs={'slug': self.slug})
    
    class Meta:
        ordering = ['-created_at']


class BlogComment(models.Model):
    """
    Blog comment model - User comments on blog posts
    """
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"
    
    class Meta:
        ordering = ['created_at']