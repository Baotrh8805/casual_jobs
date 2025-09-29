from django.db import models
from django.conf import settings
from django.utils import timezone
import datetime

class JobCategory(models.Model):
    """
    Danh mục công việc (pha chế, phục vụ bàn, bảo vệ, lễ tân, ...)
    """
    name = models.CharField(max_length=100, unique=True, help_text='Tên danh mục công việc')
    description = models.TextField(blank=True, help_text='Mô tả danh mục')
    icon = models.CharField(max_length=50, blank=True, help_text='CSS class cho icon')
    color = models.CharField(max_length=7, default='#007bff', help_text='Màu sắc hiển thị (hex)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Danh mục công việc'
        verbose_name_plural = 'Danh mục công việc'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class JobPost(models.Model):
    """
    Bài đăng việc làm
    """
    PRIORITY_CHOICES = (
        ('low', 'Thấp'),
        ('normal', 'Bình thường'),
        ('high', 'Cao'),
        ('urgent', 'Khẩn cấp'),
    )
    
    PAYMENT_TYPES = (
        ('hourly', 'Theo giờ'),
        ('daily', 'Theo ngày'),
        ('fixed', 'Cố định'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Nháp'),
        ('published', 'Đã đăng'),
        ('closed', 'Đã đóng'),
        ('expired', 'Hết hạn'),
    )
    
    # Thông tin cơ bản
    title = models.CharField(max_length=200, help_text='Tiêu đề bài đăng')
    description = models.TextField(help_text='Mô tả chi tiết công việc')
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                related_name='job_posts', limit_choices_to={'user_type': 'employer'})
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='jobs')
    
    # Địa điểm và thời gian
    location = models.CharField(max_length=200, help_text='Địa điểm làm việc')
    work_date = models.DateField(help_text='Ngày làm việc')
    work_time_start = models.TimeField(help_text='Giờ bắt đầu')
    work_time_end = models.TimeField(help_text='Giờ kết thúc')
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, 
                                        help_text='Số giờ làm việc')
    
    # Lương và thanh toán
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES, default='hourly')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, 
                                        help_text='Số tiền (VND)')
    
    # Yêu cầu
    required_skills = models.TextField(blank=True, 
                                      help_text='Kỹ năng yêu cầu (cách nhau bởi dấu phẩy)')
    experience_required = models.PositiveIntegerField(default=0, 
                                                     help_text='Số năm kinh nghiệm yêu cầu')
    number_of_workers = models.PositiveIntegerField(default=1, 
                                                   help_text='Số lượng người cần tuyển')
    
    # Trạng thái và ưu tiên
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Thời gian
    application_deadline = models.DateTimeField(null=True, blank=True, editable=False, 
                                              help_text='Không sử dụng - Sẽ tự động lấy theo thời gian bắt đầu')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Contact info
    contact_phone = models.CharField(max_length=15, blank=True)
    contact_email = models.EmailField(blank=True)
    
    class Meta:
        verbose_name = 'Bài đăng việc làm'
        verbose_name_plural = 'Bài đăng việc làm'
        ordering = ['-created_at', '-priority']
    
    def __str__(self):
        return f"{self.title} - {self.category.name}"
    
    def get_required_skills_list(self):
        """Trả về danh sách kỹ năng yêu cầu dưới dạng list"""
        return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()]
    
    def is_expired(self):
        """Kiểm tra xem bài đăng có hết hạn không (quá thời gian bắt đầu làm việc)"""
        now = timezone.now()
        work_datetime = timezone.make_aware(datetime.datetime.combine(self.work_date, self.work_time_start))
        return now >= work_datetime
    
    def calculate_total_payment(self):
        """Tính tổng tiền cho công việc"""
        if self.payment_type == 'hourly':
            return self.payment_amount * self.duration_hours
        else:
            return self.payment_amount
            
    def save(self, *args, **kwargs):
        """Tự động cập nhật application_deadline theo thời gian bắt đầu công việc"""
        # Nếu đã có ngày làm việc và giờ bắt đầu, cập nhật application_deadline
        if self.work_date and self.work_time_start:
            self.application_deadline = timezone.make_aware(
                datetime.datetime.combine(self.work_date, self.work_time_start)
            )
        super().save(*args, **kwargs)

class JobApplication(models.Model):
    """
    Đơn ứng tuyển việc làm
    """
    STATUS_CHOICES = (
        ('pending', 'Chờ xử lý'),
        ('accepted', 'Được chấp nhận'),
        ('rejected', 'Bị từ chối'),
        ('withdrawn', 'Đã rút lại'),
    )
    
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='job_applications', 
                                 limit_choices_to={'user_type': 'worker'})
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    cover_letter = models.TextField(blank=True, help_text='Thư xin việc')
    proposed_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                       help_text='Mức lương đề xuất (VND)')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Đơn ứng tuyển'
        verbose_name_plural = 'Đơn ứng tuyển'
        unique_together = ['job', 'applicant']  # Mỗi người chỉ được ứng tuyển 1 lần cho 1 job
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.applicant.username} ứng tuyển {self.job.title}"
