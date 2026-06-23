from django.urls import path
from .views import (
    submit_feedback, feedback_success, feedback_list,
    admin_feedback, approve_feedback, delete_feedback
)

urlpatterns = [
    # Public URLs
    path('', submit_feedback, name='submit_feedback'),
    path('success/', feedback_success, name='feedback_success'),
    path('list/', feedback_list, name='feedback_list'),
    
    # Admin URLs
    path('admin/', admin_feedback, name='admin_feedback'),
    path('admin/approve/<int:feedback_id>/', approve_feedback, name='approve_feedback'),
    path('admin/delete/<int:feedback_id>/', delete_feedback, name='delete_feedback'),
]