from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Job listing and detail
    path('', views.job_list_view, name='job_list'),
    path('<int:pk>/', views.job_detail_view, name='job_detail'),
    
    # Job management for employers
    path('create/', views.job_create_view, name='job_create'),
    path('<int:pk>/edit/', views.job_edit_view, name='job_edit'),
    path('my-jobs/', views.my_jobs_view, name='my_jobs'),
    
    # Job applications for workers
    path('<int:pk>/apply/', views.job_apply_view, name='job_apply'),
    path('my-applications/', views.my_applications_view, name='my_applications'),
    
    # Application management for employers
    path('applications/<int:pk>/accept/', views.accept_application_view, name='accept_application'),
    path('applications/<int:pk>/reject/', views.reject_application_view, name='reject_application'),
]