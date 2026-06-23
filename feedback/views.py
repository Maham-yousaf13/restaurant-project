from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .models import Feedback
from .forms import FeedbackForm


def submit_feedback(request):
    """
    Submit customer feedback
    """
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            
            # Set user if logged in
            if request.user.is_authenticated:
                feedback.user = request.user
                
            # If user has an order, link it (optional)
            # feedback.order = Order.objects.filter(user=request.user).first()
            
            feedback.save()
            messages.success(request, 'Thank you for your feedback! We value your opinion.')
            return redirect('feedback_success')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FeedbackForm()
        
        # Pre-fill form if user is logged in
        if request.user.is_authenticated:
            form.fields['name'].initial = request.user.get_full_name() or request.user.username
            form.fields['email'].initial = request.user.email
    
    context = {
        'form': form,
    }
    return render(request, 'feedback/submit.html', context)


def feedback_success(request):
    """
    Feedback success page
    """
    return render(request, 'feedback/success.html')


def feedback_list(request):
    """
    Public feedback list - shows only approved feedbacks
    """
    feedbacks = Feedback.objects.filter(is_approved=True)
    context = {
        'feedbacks': feedbacks,
    }
    return render(request, 'feedback/list.html', context)


@staff_member_required
def admin_feedback(request):
    """
    Admin feedback management page
    """
    feedbacks = Feedback.objects.all().order_by('-created_at')
    
    # Filter by approval status
    status = request.GET.get('status')
    if status == 'approved':
        feedbacks = feedbacks.filter(is_approved=True)
    elif status == 'pending':
        feedbacks = feedbacks.filter(is_approved=False)
    
    context = {
        'feedbacks': feedbacks,
        'status': status,
    }
    return render(request, 'feedback/admin.html', context)


@staff_member_required
def approve_feedback(request, feedback_id):
    """
    Approve a feedback
    """
    feedback = get_object_or_404(Feedback, id=feedback_id)
    feedback.is_approved = True
    feedback.save()
    messages.success(request, f'Feedback from {feedback.name} approved successfully!')
    return redirect('admin_feedback')


@staff_member_required
def delete_feedback(request, feedback_id):
    """
    Delete a feedback
    """
    feedback = get_object_or_404(Feedback, id=feedback_id)
    name = feedback.name
    feedback.delete()
    messages.success(request, f'Feedback from {name} deleted successfully!')
    return redirect('admin_feedback')