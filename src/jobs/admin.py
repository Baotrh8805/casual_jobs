from django.contrib import admin
from .models import JobCategory, JobPost, JobApplication

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    """Admin configuration cho JobCategory"""
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Hiển thị', {
            'fields': ('icon', 'color'),
            'description': 'Tùy chỉnh cách hiển thị danh mục trên website'
        }),
    )

@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    """Admin configuration cho JobPost"""
    list_display = ('title', 'employer', 'category', 'location', 'work_date', 'payment_amount', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'category', 'payment_type', 'work_date', 'created_at')
    search_fields = ('title', 'description', 'location', 'employer__username', 'required_skills')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('title', 'description', 'employer', 'category', 'status', 'priority')
        }),
        ('Địa điểm và thời gian', {
            'fields': ('location', 'work_date', 'work_time_start', 'work_time_end', 'duration_hours')
        }),
        ('Lương và thanh toán', {
            'fields': ('payment_type', 'payment_amount')
        }),
        ('Yêu cầu công việc', {
            'fields': ('required_skills', 'experience_required', 'number_of_workers')
        }),
        ('Thông tin liên hệ', {
            'fields': ('contact_phone', 'contact_email', 'application_deadline')
        }),
        ('Thời gian hệ thống', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('employer', 'category')

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """Admin configuration cho JobApplication"""
    list_display = ('applicant', 'job', 'status', 'proposed_rate', 'applied_at')
    list_filter = ('status', 'applied_at', 'job__category')
    search_fields = ('applicant__username', 'job__title', 'cover_letter')
    ordering = ('-applied_at',)
    readonly_fields = ('applied_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('job', 'applicant', 'status')
        }),
        ('Thông tin ứng tuyển', {
            'fields': ('cover_letter', 'proposed_rate')
        }),
        ('Thời gian', {
            'fields': ('applied_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('applicant', 'job', 'job__category')

# Tùy chỉnh Django Admin interface
admin.site.site_header = 'CasualJobs Admin'
admin.site.site_title = 'CasualJobs Admin'
admin.site.index_title = 'Quản trị hệ thống kết nối việc làm casual'
