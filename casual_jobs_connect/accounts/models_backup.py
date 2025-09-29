from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model mở rộng từ AbstractUser
    """
    USER_TYPES = (
        ('employer', 'Nhà tuyển dụng'),
        ('worker', 'Người tìm việc'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='worker')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def get_accepted_applications_count(self):
        """Đếm số đơn ứng tuyển được chấp nhận"""
        return self.job_applications.filter(status='accepted').count()
    
    def get_total_applications_count(self):
        """Đếm tổng số đơn ứng tuyển"""
        return self.job_applications.count()

class UserProfile(models.Model):
    """
    Hồ sơ chi tiết của người dùng
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, help_text='Giới thiệu bản thân')
    skills = models.TextField(blank=True, help_text='Kỹ năng (cách nhau bởi dấu phẩy)')
    experience_years = models.PositiveIntegerField(default=0, help_text='Số năm kinh nghiệm')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, 
                                     help_text='Mức lương theo giờ (VND)')
    availability = models.TextField(blank=True, help_text='Thời gian có thể làm việc')
    is_available = models.BooleanField(default=True, help_text='Đang tìm việc')
    
    def __str__(self):
        return f"Profile của {self.user.username}"

    def get_skills_list(self):
        """Trả về danh sách kỹ năng dưới dạng list"""
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
