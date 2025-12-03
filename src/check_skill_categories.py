"""
Script kiểm tra danh mục của kỹ năng
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'casual_jobs_connect.settings')
django.setup()

from accounts.models import Skill
from jobs.models import JobCategory

print("=" * 80)
print("KIỂM TRA DANH MỤC CỦA KỸ NĂNG")
print("=" * 80)

# Lấy tất cả danh mục công việc
all_job_categories = JobCategory.objects.all()
print(f"\n📋 Danh sách danh mục công việc trong database ({all_job_categories.count()}):")
print("-" * 80)
job_category_names = set()
for cat in all_job_categories:
    job_category_names.add(cat.name)
    print(f"  • {cat.name}")

# Lấy tất cả kỹ năng
all_skills = Skill.objects.all()
print(f"\n🔧 Tổng số kỹ năng: {all_skills.count()}")

# Lấy danh sách các danh mục được sử dụng trong kỹ năng
skill_categories = Skill.objects.exclude(category='').values_list('category', flat=True).distinct()
print(f"\n📂 Danh mục được sử dụng trong kỹ năng ({len(skill_categories)}):")
print("-" * 80)
for cat in skill_categories:
    count = Skill.objects.filter(category=cat).count()
    print(f"  • {cat:30} ({count} kỹ năng)")

# Tìm các danh mục trong kỹ năng nhưng không tồn tại trong JobCategory
print(f"\n⚠️  DANH MỤC KHÔNG KHỚ̉P:")
print("-" * 80)
invalid_categories = []
for cat in skill_categories:
    if cat not in job_category_names:
        count = Skill.objects.filter(category=cat).count()
        invalid_categories.append(cat)
        print(f"  ❌ '{cat}' - Có {count} kỹ năng nhưng KHÔNG TỒN TẠI trong JobCategory")

if not invalid_categories:
    print("  ✅ Tất cả danh mục kỹ năng đều tồn tại trong JobCategory")

# Hiển thị chi tiết các kỹ năng có danh mục không hợp lệ
if invalid_categories:
    print(f"\n📝 CHI TIẾT CÁC KỸ NĂNG CÓ DANH MỤC KHÔNG HỢP LỆ:")
    print("-" * 80)
    for cat in invalid_categories:
        print(f"\nDanh mục: '{cat}'")
        skills = Skill.objects.filter(category=cat)
        for skill in skills:
            status = "Hoạt động" if skill.is_active else "Không hoạt động"
            print(f"  • {skill.name:30} [{status}]")

# Đề xuất giải pháp
if invalid_categories:
    print(f"\n💡 ĐỀ XUẤT GIẢI PHÁP:")
    print("-" * 80)
    print("1. Tạo các danh mục JobCategory mới cho:")
    for cat in invalid_categories:
        print(f"   - {cat}")
    print("\n2. Hoặc cập nhật category của các kỹ năng này sang danh mục đã tồn tại")
    print("\n3. Mapping gợi ý:")
    
    mapping_suggestions = {
        'sales': 'Bán hàng',
        'event': 'Sự kiện',
        'warehouse': 'Giao hàng',  # hoặc tạo mới 'Kho vận'
        'care': 'Phục vụ bàn',  # hoặc tạo mới 'Chăm sóc'
        'creative': 'Sự kiện',  # hoặc tạo mới 'Sáng tạo'
        'cleaning': 'Tạp vụ',  # hoặc tạo mới 'Dọn dẹp'
        'delivery': 'Giao hàng',
        'office': 'Lễ tân',  # hoặc tạo mới 'Văn phòng'
        'language': 'Lễ tân',  # Hoặc category phù hợp khác
        'technical': 'Tạp vụ',  # Hoặc category phù hợp khác
        'restaurant': 'Phục vụ bàn',
    }
    
    for old_cat in invalid_categories:
        if old_cat in mapping_suggestions:
            print(f"   • '{old_cat}' → '{mapping_suggestions[old_cat]}'")

print("\n" + "=" * 80)
