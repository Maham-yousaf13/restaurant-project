from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import BlogPost, BlogCategory, BlogComment
from .serializers import (
    BlogPostSerializer, BlogCategorySerializer, 
    BlogCommentSerializer
)


# ==================== API VIEWS ====================

class BlogCategoryViewSet(viewsets.ModelViewSet):
    """
    Blog Category API (CRUD)
    """
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class BlogPostViewSet(viewsets.ModelViewSet):
    """
    Blog Post API (CRUD)
    """
    queryset = BlogPost.objects.filter(is_published=True)
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'content', 'category__name']
    ordering_fields = ['created_at', 'views']
    filterset_fields = ['category', 'is_published', 'is_featured']
    
    def get_queryset(self):
        """
        Show all posts for admin/owner, only published for others
        """
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.is_restaurant_owner):
            return BlogPost.objects.all()
        return BlogPost.objects.filter(is_published=True)
    
    def perform_create(self, serializer):
        """
        Set author when creating post
        """
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """
        Add comment to a blog post
        """
        post = self.get_object()
        content = request.data.get('content')
        
        if not content:
            return Response(
                {'error': 'Content required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Login required to comment'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        comment = BlogComment.objects.create(
            post=post,
            user=request.user,
            content=content,
            is_approved=True  # Auto-approve for now
        )
        
        serializer = BlogCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        """
        Increment blog post views
        """
        post = self.get_object()
        post.views += 1
        post.save()
        return Response({'views': post.views})
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured blog posts
        """
        featured_posts = BlogPost.objects.filter(
            is_published=True,
            is_featured=True
        )[:5]
        serializer = self.get_serializer(featured_posts, many=True)
        return Response(serializer.data)


class BlogCommentViewSet(viewsets.ModelViewSet):
    """
    Blog Comment API (CRUD)
    """
    queryset = BlogComment.objects.filter(is_approved=True)
    serializer_class = BlogCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        """
        Set user when creating comment
        """
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['patch'])
    def approve_comment(self, request, pk=None):
        """
        Approve a comment
        """
        comment = self.get_object()
        comment.is_approved = True
        comment.save()
        return Response({'message': 'Comment approved'})


# ==================== FRONTEND VIEWS ====================

def blog_list(request):
    """
    Display all blog posts with categories
    """
    posts = BlogPost.objects.filter(is_published=True)
    categories = BlogCategory.objects.all()
    
    # Get category filter from URL
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Get search query
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    context = {
        'posts': posts,
        'categories': categories,
        'active_category': category_slug,
        'search_query': search_query,
    }
    return render(request, 'blog/list.html', context)


def blog_detail(request, slug):
    """
    Display single blog post with comments
    """
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Increment views
    post.views += 1
    post.save()
    
    # Get approved comments
    comments = post.comments.filter(is_approved=True)
    
    # Handle comment submission
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        if content:
            BlogComment.objects.create(
                post=post,
                user=request.user,
                content=content,
                is_approved=True  # Auto-approve for now
            )
            messages.success(request, 'Comment added successfully!')
            return redirect('blog_detail', slug=post.slug)
        else:
            messages.error(request, 'Please write a comment.')
    
    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'blog/detail.html', context)


@login_required
def admin_blog_posts(request):
    """
    Admin blog management page
    """
    if not (request.user.is_staff or request.user.is_restaurant_owner):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    posts = BlogPost.objects.all().order_by('-created_at')
    
    context = {
        'posts': posts,
    }
    return render(request, 'blog/admin_posts.html', context)


@login_required
def admin_blog_create(request):
    """
    Create new blog post
    """
    if not (request.user.is_staff or request.user.is_restaurant_owner):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        content = request.POST.get('content')
        excerpt = request.POST.get('excerpt')
        category_id = request.POST.get('category')
        is_published = request.POST.get('is_published') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'
        
        # Validate slug
        if not slug:
            import re
            slug = re.sub(r'[^a-z0-9]+', '-', title.lower())
        
        # Check if slug exists
        if BlogPost.objects.filter(slug=slug).exists():
            messages.error(request, 'Slug already exists. Please use a different one.')
            return render(request, 'blog/admin_create.html', {'categories': BlogCategory.objects.all()})
        
        # Create post
        post = BlogPost.objects.create(
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt,
            category_id=category_id if category_id else None,
            author=request.user,
            is_published=is_published,
            is_featured=is_featured,
        )
        
        messages.success(request, f'Blog post "{title}" created successfully!')
        return redirect('admin_blog_posts')
    
    context = {
        'categories': BlogCategory.objects.all(),
    }
    return render(request, 'blog/admin_create.html', context)


@login_required
def admin_blog_edit(request, post_id):
    """
    Edit blog post
    """
    if not (request.user.is_staff or request.user.is_restaurant_owner):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    post = get_object_or_404(BlogPost, id=post_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        content = request.POST.get('content')
        excerpt = request.POST.get('excerpt')
        category_id = request.POST.get('category')
        is_published = request.POST.get('is_published') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'
        
        # Validate slug uniqueness (excluding current post)
        if BlogPost.objects.filter(slug=slug).exclude(id=post.id).exists():
            messages.error(request, 'Slug already exists. Please use a different one.')
            return render(request, 'blog/admin_edit.html', {
                'post': post,
                'categories': BlogCategory.objects.all()
            })
        
        # Update post
        post.title = title
        post.slug = slug
        post.content = content
        post.excerpt = excerpt
        post.category_id = category_id if category_id else None
        post.is_published = is_published
        post.is_featured = is_featured
        post.save()
        
        messages.success(request, f'Blog post "{title}" updated successfully!')
        return redirect('admin_blog_posts')
    
    context = {
        'post': post,
        'categories': BlogCategory.objects.all(),
    }
    return render(request, 'blog/admin_edit.html', context)


@login_required
def admin_blog_delete(request, post_id):
    """
    Delete blog post
    """
    if not (request.user.is_staff or request.user.is_restaurant_owner):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    post = get_object_or_404(BlogPost, id=post_id)
    title = post.title
    post.delete()
    messages.success(request, f'Blog post "{title}" deleted successfully!')
    return redirect('admin_blog_posts')