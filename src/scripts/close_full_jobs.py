"""
Script đóng các công việc đã đủ người
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'casual_jobs_connect.settings')
django.setup()

from jobs.models import JobPost, JobApplication
from django.db.models import Count

print("=" * 80)
print("KIỂM TRA VÀ ĐÓNG CÁC CÔNG VIỆC ĐÃ ĐỦ NGƯỜI")
print("=" * 80)

# Lấy tất cả công việc đang published
published_jobs = JobPost.objects.filter(status='published')

print(f"\nTổng số công việc đang đăng: {published_jobs.count()}\n")

closed_count = 0
for job in published_jobs:
    # Đếm số người đã được chấp nhận
    accepted_count = JobApplication.objects.filter(
        job=job,
        status='accepted'
    ).count()
    
    print(f"Job #{job.id}: {job.title[:50]}")
    print(f"  - Cần tuyển: {job.number_of_workers}")
    print(f"  - Đã chấp nhận: {accepted_count}")
    
    # Nếu đủ người -> đóng công việc
    if accepted_count >= job.number_of_workers:
        job.status = 'closed'
        job.save()
        closed_count += 1
        print(f"  ✅ ĐÃ ĐÓNG (đủ {job.number_of_workers} người)")
        
        # Từ chối các đơn còn lại
        pending_apps = JobApplication.objects.filter(
            job=job,
            status='pending'
        )
        rejected_count = pending_apps.count()
        if rejected_count > 0:
            pending_apps.update(status='rejected')
            print(f"  ✅ Đã từ chối {rejected_count} đơn còn lại")
    else:
        remaining = job.number_of_workers - accepted_count
        print(f"  ⏳ Còn cần {remaining} người")
    
    print()

print("=" * 80)
print(f"✅ HOÀN TẤT! Đã đóng {closed_count} công việc")
print("=" * 80)
