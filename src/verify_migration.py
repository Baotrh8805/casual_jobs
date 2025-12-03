"""
Script kiểm tra danh mục của kỹ năng sau khi migrate
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'casual_jobs_connect.settings')
django.setup()

from accounts.models import Skill
from jobs.models import JobCategory

print("=" * 80)
print("KIỂM TRA DANH MỤC CỦA KỸ NĂNG SAU KHI MIGRATE")
print("=" * 80)

# Lấy tất cả danh mục công việc
all_job_categories = JobCategory.objects.all().order_by('name')
print(f"\n📋 Danh sách danh mục công việc trong database ({all_job_categories.count()}):")
print("-" * 80)
for cat in all_job_categories:
    skill_count = cat.skills.count()
    icon = f"{cat.icon}" if cat.icon else "Chưa có"
    print(f"  • {cat.name:20} ({skill_count:2} kỹ năng) - Icon: {icon:20} - Màu: {cat.color}")

# Lấy tất cả kỹ năng
all_skills = Skill.objects.select_related('category').all()
print(f"\n🔧 Tổng số kỹ năng: {all_skills.count()}")

# Thống kê kỹ năng theo danh mục
print(f"\n📊 THỐNG KÊ KỸ NĂNG THEO DANH MỤC:")
print("-" * 80)

skills_with_category = all_skills.filter(category__isnull=False)
skills_without_category = all_skills.filter(category__isnull=True)

print(f"  ✅ Kỹ năng có danh mục: {skills_with_category.count()}")
print(f"  ⚠️  Kỹ năng chưa có danh mục: {skills_without_category.count()}")

if skills_without_category.exists():
    print(f"\n❌ DANH SÁCH KỸ NĂNG CHƯA CÓ DANH MỤC:")
    print("-" * 80)
    for skill in skills_without_category:
        print(f"  • {skill.name}")

print(f"\n✅ CHI TIẾT KỸ NĂNG THEO DANH MỤC:")
print("-" * 80)
for category in all_job_categories:
    skills = category.skills.filter(is_active=True)
    if skills.exists():
        print(f"\n{category.name} ({skills.count()} kỹ năng):")
        for skill in skills:
            print(f"  • {skill.name}")

print("\n" + "=" * 80)
print("✅ HOÀN TẤT KIỂM TRA!")
print("=" * 80)
