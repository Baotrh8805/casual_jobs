"""
Script sửa lỗi danh mục kỹ năng
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'casual_jobs_connect.settings')
django.setup()

from accounts.models import Skill
from jobs.models import JobCategory

print("=" * 80)
print("SỬA LỖI DANH MỤC KỸ NĂNG")
print("=" * 80)

# Bước 1: Tạo các danh mục JobCategory còn thiếu
print("\n📝 BƯỚC 1: Tạo các danh mục JobCategory còn thiếu")
print("-" * 80)

new_categories = [
    {
        'name': 'Kho vận',
        'icon': 'bi-box-seam',
        'color': '#3498DB',
        'description': 'Nhân viên kho, bốc vác, đóng gói, kiểm kê hàng hóa'
    },
    {
        'name': 'Chăm sóc',
        'icon': 'bi-heart',
        'color': '#E91E63',
        'description': 'Chăm sóc người già, trẻ em, thú cưng'
    },
    {
        'name': 'Sáng tạo',
        'icon': 'bi-camera',
        'color': '#9C27B0',
        'description': 'Chụp ảnh, quay phim, thiết kế'
    },
    {
        'name': 'Dọn dẹp',
        'icon': 'bi-droplet',
        'color': '#00BCD4',
        'description': 'Dọn dẹp, vệ sinh, giặt ủi'
    },
    {
        'name': 'Văn phòng',
        'icon': 'bi-file-earmark-text',
        'color': '#607D8B',
        'description': 'Hỗ trợ văn phòng, nhập liệu, in ấn'
    },
]

created_count = 0
for cat_data in new_categories:
    cat, created = JobCategory.objects.get_or_create(
        name=cat_data['name'],
        defaults={
            'icon': cat_data['icon'],
            'color': cat_data['color'],
            'description': cat_data['description']
        }
    )
    if created:
        print(f"  ✅ Đã tạo: {cat.name} ({cat.icon})")
        created_count += 1
    else:
        print(f"  ℹ️  Đã tồn tại: {cat.name}")

print(f"\n✅ Đã tạo {created_count} danh mục mới")

# Bước 2: Cập nhật danh mục cho kỹ năng
print("\n📝 BƯỚC 2: Cập nhật danh mục cho kỹ năng")
print("-" * 80)

# Mapping từ danh mục cũ sang danh mục mới
category_mapping = {
    'restaurant': 'Phục vụ bàn',
    'technical': 'Tạp vụ',
    'language': 'Lễ tân',
}

updated_count = 0
for old_cat, new_cat in category_mapping.items():
    skills = Skill.objects.filter(category=old_cat)
    count = skills.count()
    if count > 0:
        skills.update(category=new_cat)
        print(f"  ✅ '{old_cat}' → '{new_cat}' ({count} kỹ năng)")
        updated_count += count

print(f"\n✅ Đã cập nhật {updated_count} kỹ năng")

# Bước 3: Kiểm tra lại
print("\n📝 BƯỚC 3: Kiểm tra lại")
print("-" * 80)

# Lấy tất cả danh mục công việc
all_job_categories = JobCategory.objects.all()
job_category_names = set(cat.name for cat in all_job_categories)

# Lấy danh sách các danh mục được sử dụng trong kỹ năng
skill_categories = Skill.objects.exclude(category='').values_list('category', flat=True).distinct()

# Tìm các danh mục trong kỹ năng nhưng không tồn tại trong JobCategory
invalid_categories = []
for cat in skill_categories:
    if cat not in job_category_names:
        count = Skill.objects.filter(category=cat).count()
        invalid_categories.append((cat, count))

if invalid_categories:
    print("  ⚠️  Vẫn còn danh mục không hợp lệ:")
    for cat, count in invalid_categories:
        print(f"    ❌ '{cat}' ({count} kỹ năng)")
else:
    print("  ✅ Tất cả danh mục kỹ năng đều hợp lệ!")

# Hiển thị thống kê
print("\n📊 THỐNG KÊ CUỐI CÙNG:")
print("-" * 80)
print(f"  • Tổng số JobCategory: {all_job_categories.count()}")
print(f"  • Tổng số kỹ năng: {Skill.objects.count()}")
print(f"  • Số danh mục được sử dụng: {len(skill_categories)}")

print("\n📋 Danh mục và số lượng kỹ năng:")
for cat in sorted(skill_categories):
    count = Skill.objects.filter(category=cat).count()
    print(f"  • {cat:20} - {count:2} kỹ năng")

print("\n" + "=" * 80)
print("✅ HOÀN THÀNH!")
print("=" * 80)
