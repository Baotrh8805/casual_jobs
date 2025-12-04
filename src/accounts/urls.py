from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    
    # API endpoints for real-time validation
    path('check-username/', views.check_username, name='check_username'),
    path('check-email/', views.check_email, name='check_email'),
    path('check-phone/', views.check_phone, name='check_phone'),
    
    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/dashboard/', views.admin_dashboard),  # URL cũ (để tương thích)
    path('admin_dashboard/', views.admin_dashboard),  # Thêm URL mới
    path('admin/skills/', views.admin_skills_management, name='admin_skills'),
    path('admin/categories/', views.admin_categories_management, name='admin_categories'),
    path('admin/applications/', views.admin_applications, name='admin_applications'),
    path('admin/complaints/', views.admin_complaints, name='admin_complaints'),
    path('admin/complaints/<int:complaint_id>/', views.admin_complaint_detail, name='admin_complaint_detail'),
    path('admin/users/', views.admin_user_management, name='admin_users'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('api/notifications/unread-count/', views.get_unread_notifications_count, name='unread_notifications_count'),
    path('api/notifications/recent/', views.get_recent_notifications, name='recent_notifications'),
    path('api/schedule/', views.get_work_schedule, name='work_schedule'),
]