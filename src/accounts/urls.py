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
    path('admin/complaints/', views.admin_complaints, name='admin_complaints'),
    path('admin/complaints/<int:complaint_id>/', views.admin_complaint_detail, name='admin_complaint_detail'),
    path('admin/users/', views.admin_user_management, name='admin_users'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
]
