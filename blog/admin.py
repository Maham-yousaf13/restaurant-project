from django.contrib import admin
from .models import BlogCategory, BlogPost, BlogComment


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Blog Category
    """
    list_display = ('name', 'slug', 'post_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    
    def post_count(self, obj):
        """
        Count posts in this category
        """
        return obj.posts.filter(is_published=True).count()
    post_count.short_description = 'Posts'


class BlogCommentInline(admin.TabularInline):
    """
    Inline comments in blog post admin
    """
    model = BlogComment
    extra = 1
    fields = ('user', 'content', 'is_approved', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """
    Admin configuration for Blog Post
    """
    list_display = ('title', 'category', 'author', 'is_published', 'is_featured', 'views', 'created_at')
    list_filter = ('is_published', 'is_featured', 'category', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views', 'created_at', 'updated_at')
    inlines = [BlogCommentInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'content', 'excerpt')
        }),
        ('Category & Author', {
            'fields': ('category', 'author')
        }),
        ('Media', {
            'fields': ('featured_image',)
        }),
        ('Status', {
            'fields': ('is_published', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('views', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Auto-set author when creating post
        """
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Blog Comment
    """
    list_display = ('user', 'post', 'content_preview', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'content', 'post__title')
    actions = ['approve_comments', 'unapprove_comments']
    
    def content_preview(self, obj):
        """
        Show truncated comment content in list
        """
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Comment'
    
    def approve_comments(self, request, queryset):
        """
        Bulk approve comments
        """
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"
    
    def unapprove_comments(self, request, queryset):
        """
        Bulk unapprove comments
        """
        queryset.update(is_approved=False)
    unapprove_comments.short_description = "Unapprove selected comments"