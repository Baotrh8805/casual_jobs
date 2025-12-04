"""
Script cập nhật icon và màu cho danh mục công việc
Chạy: python update_category_icons.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'casual_jobs_connect.settings')
django.setup()

from jobs.models import JobCategory

# Định nghĩa icon và màu cho các danh mục
category_icons = {
    'Pha chế': {
        'icon': 'bi-cup-hot',
        'color': '#8B4513',  # Màu nâu cafe
        'description': 'Pha chế đồ uống, bartender, barista'
    },
    'Phục vụ bàn': {
        'icon': 'bi-person-check',
        'color': '#FF6B6B',  # Màu đỏ cam
        'description': 'Phục vụ nhà hàng, quán cafe'
    },
    'Bảo vệ': {
        'icon': 'bi-shield-check',
        'color': '#4ECDC4',  # Màu xanh ngọc
        'description': 'Bảo vệ, an ninh'
    },
    'Lễ tân': {
        'icon': 'bi-person-badge',
        'color': '#9B59B6',  # Màu tím
        'description': 'Lễ tân, tiếp tân'
    },
    'Giao hàng': {
        'icon': 'bi-truck',
        'color': '#F39C12',  # Màu cam
        'description': 'Giao hàng, shipper'
    },
    'Kho vận': {
        'icon': 'bi-box-seam',
        'color': '#3498DB',  # Màu xanh dương
        'description': 'Nhân viên kho, đóng gói'
    },
    'Bán hàng': {
        'icon': 'bi-cart',
        'color': '#E74C3C',  # Màu đỏ
        'description': 'Bán hàng, sales'
    },
    'Làm vườn': {
        'icon': 'bi-tree',
        'color': '#27AE60',  # Màu xanh lá
        'description': 'Làm vườn, chăm sóc cây'
    },
}

print("Đang cập nhật icon và màu cho danh mục công việc...")
print("=" * 60)

updated_count = 0
for category_name, data in category_icons.items():
    try:
        category = JobCategory.objects.get(name=category_name)
        category.icon = data['icon']
        category.color = data['color']
        if not category.description:
            category.description = data['description']
        category.save()
        
        print(f"✓ {category_name:20} → {data['icon']:20} {data['color']}")
        updated_count += 1
    except JobCategory.DoesNotExist:
        print(f"✗ {category_name:20} → Chưa tồn tại trong database")

print("=" * 60)
print(f"\n✅ Hoàn thành! Đã cập nhật {updated_count}/{len(category_icons)} danh mục.")

# Hiển thị danh sách tất cả danh mục hiện có
print("\n📋 Danh sách tất cả danh mục trong database:")
print("-" * 60)
all_categories = JobCategory.objects.all()
for cat in all_categories:
    icon_display = cat.icon if cat.icon else '(chưa có)'
    color_display = cat.color if cat.color else '(chưa có)'
    print(f"  • {cat.name:20} | Icon: {icon_display:20} | Màu: {color_display}")
