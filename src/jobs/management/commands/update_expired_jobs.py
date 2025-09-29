from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime
from jobs.models import JobPost

class Command(BaseCommand):
    help = 'Cập nhật trạng thái công việc quá hạn ứng tuyển (quá thời gian bắt đầu làm việc)'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        
        # Lấy các công việc đã đăng nhưng chưa đóng
        active_jobs = JobPost.objects.filter(status='published')
        
        updated_count = 0
        for job in active_jobs:
            # Tạo datetime từ ngày làm việc và giờ bắt đầu
            work_datetime = timezone.make_aware(
                datetime.datetime.combine(job.work_date, job.work_time_start)
            )
            
            # Nếu đã quá thời gian bắt đầu, cập nhật trạng thái
            if now >= work_datetime:
                job.status = 'closed'
                job.save(update_fields=['status'])
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Đã đóng {updated_count} công việc quá hạn ứng tuyển')
        )