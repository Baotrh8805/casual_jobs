from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Skill(models.Model):
    """
    Danh sách kỹ năng có sẵn
    """
    name = models.CharField(max_length=100, unique=True, help_text='Tên kỹ năng')
    normalized_name = models.CharField(max_length=100, unique=True, help_text='Tên chuẩn hóa')
    category = models.CharField(max_length=50, blank=True, help_text='Danh mục kỹ năng')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Kỹ năng'
        verbose_name_plural = 'Kỹ năng'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        # Tự động chuẩn hóa tên (lowercase, trim)
        self.normalized_name = self.name.lower().strip()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class User(AbstractUser):
    """
    Custom User model mở rộng từ AbstractUser
    """
    USER_TYPES = (
        ('employer', 'Nhà tuyển dụng'),
        ('worker', 'Người tìm việc'),
        ('admin', 'Quản trị viên'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='worker')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False, help_text='Tài khoản đã xác thực')
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def get_accepted_applications_count(self):
        """Đếm số đơn ứng tuyển được chấp nhận"""
        return self.job_applications.filter(status='accepted').count()
    
    def get_total_applications_count(self):
        """Đếm tổng số đơn ứng tuyển"""
        return self.job_applications.count()
    
    def is_admin(self):
        """Kiểm tra có phải admin không"""
        return self.user_type == 'admin' or self.is_superuser

class UserProfile(models.Model):
    """
    Hồ sơ chi tiết của người dùng
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, help_text='Giới thiệu bản thân')
    skills = models.ManyToManyField(Skill, blank=True, help_text='Kỹ năng có sẵn')
    custom_skills = models.TextField(blank=True, help_text='Kỹ năng tự do (cách nhau bởi dấu phẩy)')
    experience_years = models.PositiveIntegerField(default=0, help_text='Số năm kinh nghiệm')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, 
                                     help_text='Mức lương theo giờ (VND)')
    availability = models.TextField(blank=True, help_text='Thời gian có thể làm việc')
    is_available = models.BooleanField(default=True, help_text='Đang tìm việc')
    
    def __str__(self):
        return f"Profile của {self.user.username}"

    def get_skills_list(self):
        """Trả về danh sách kỹ năng dưới dạng list"""
        skills_list = []
        # Thêm skills có sẵn
        for skill in self.skills.all():
            skills_list.append(skill.name)
        # Thêm custom skills
        if self.custom_skills:
            custom_list = [skill.strip() for skill in self.custom_skills.split(',') if skill.strip()]
            skills_list.extend(custom_list)
        return skills_list
    
    def get_all_skills_normalized(self):
        """Trả về danh sách skills đã chuẩn hóa để tìm kiếm"""
        skills_list = []
        # Thêm skills có sẵn (đã chuẩn hóa)
        for skill in self.skills.all():
            skills_list.append(skill.normalized_name)
        # Thêm custom skills (chuẩn hóa)
        if self.custom_skills:
            custom_list = [skill.lower().strip() for skill in self.custom_skills.split(',') if skill.strip()]
            skills_list.extend(custom_list)
        return skills_list

class Complaint(models.Model):
    """
    Model quản lý khiếu nại
    """
    STATUS_CHOICES = (
        ('pending', 'Chờ xử lý'),
        ('in_progress', 'Đang xử lý'),
        ('resolved', 'Đã giải quyết'),
        ('rejected', 'Từ chối'),
    )
    
    TYPE_CHOICES = (
        ('job_posting', 'Bài đăng việc làm'),
        ('user_behavior', 'Hành vi người dùng'),
        ('payment', 'Thanh toán'),
        ('technical', 'Kỹ thuật'),
        ('other', 'Khác'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=200, help_text='Tiêu đề khiếu nại')
    description = models.TextField(help_text='Mô tả chi tiết')
    complaint_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text='Ghi chú của admin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Khiếu nại'
        verbose_name_plural = 'Khiếu nại'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class AdminActivity(models.Model):
    """
    Model ghi lại hoạt động của admin
    """
    ACTION_CHOICES = (
        ('user_verified', 'Xác thực người dùng'),
        ('user_banned', 'Cấm người dùng'),
        ('complaint_resolved', 'Giải quyết khiếu nại'),
        ('skill_added', 'Thêm kỹ năng'),
        ('skill_updated', 'Cập nhật kỹ năng'),
        ('system_config', 'Cấu hình hệ thống'),
        ('data_export', 'Xuất dữ liệu'),
    )
    
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_activities')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField()
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='admin_actions_against')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Hoạt động Admin'
        verbose_name_plural = 'Hoạt động Admin'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.admin.username} - {self.get_action_display()}"
