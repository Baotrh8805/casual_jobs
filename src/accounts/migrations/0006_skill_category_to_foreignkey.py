# Generated manually on 2025-12-03
import django.db.models.deletion
from django.db import migrations, models


def migrate_category_data(apps, schema_editor):
    """Chuyển dữ liệu từ category (CharField) sang category_new (ForeignKey)"""
    Skill = apps.get_model('accounts', 'Skill')
    JobCategory = apps.get_model('jobs', 'JobCategory')
    
    # Mapping từ tên category cũ (tiếng Anh) sang tên mới (tiếng Việt)
    category_mapping = {
        'restaurant': 'Phục vụ bàn',
        'technical': 'Tạp vụ',
        'language': 'Lễ tân',
        'sales': 'Bán hàng',
        'event': 'Sự kiện',
        'warehouse': 'Kho vận',
        'care': 'Chăm sóc',
        'creative': 'Sáng tạo',
        'cleaning': 'Dọn dẹp',
        'delivery': 'Giao hàng',
        'office': 'Văn phòng',
        # Các danh mục tiếng Việt giữ nguyên
        'Bán hàng': 'Bán hàng',
        'Sự kiện': 'Sự kiện',
        'Kho vận': 'Kho vận',
        'Chăm sóc': 'Chăm sóc',
        'Sáng tạo': 'Sáng tạo',
        'Dọn dẹp': 'Dọn dẹp',
        'Giao hàng': 'Giao hàng',
        'Văn phòng': 'Văn phòng',
        'Phục vụ bàn': 'Phục vụ bàn',
        'Pha chế': 'Pha chế',
        'Bảo vệ': 'Bảo vệ',
        'Lễ tân': 'Lễ tân',
        'Tạp vụ': 'Tạp vụ',
    }
    
    # Tạo các JobCategory còn thiếu
    missing_categories = {
        'Kho vận': {'icon': 'bi-box-seam', 'color': '#3498DB', 'description': 'Nhân viên kho, bốc vác, đóng gói'},
        'Chăm sóc': {'icon': 'bi-heart', 'color': '#E91E63', 'description': 'Chăm sóc người già, trẻ em, thú cưng'},
        'Sáng tạo': {'icon': 'bi-camera', 'color': '#9C27B0', 'description': 'Chụp ảnh, quay phim, thiết kế'},
        'Dọn dẹp': {'icon': 'bi-droplet', 'color': '#00BCD4', 'description': 'Dọn dẹp, vệ sinh, giặt ủi'},
        'Văn phòng': {'icon': 'bi-file-earmark-text', 'color': '#607D8B', 'description': 'Hỗ trợ văn phòng, nhập liệu'},
    }
    
    for cat_name, cat_data in missing_categories.items():
        JobCategory.objects.get_or_create(
            name=cat_name,
            defaults={
                'icon': cat_data['icon'],
                'color': cat_data['color'],
                'description': cat_data['description'],
                'is_active': True,
            }
        )
    
    # Chuyển đổi dữ liệu
    for skill in Skill.objects.all():
        if skill.category_old:  # category_old là CharField cũ
            # Map sang tên danh mục mới
            new_category_name = category_mapping.get(skill.category_old.strip(), skill.category_old.strip())
            
            # Tìm JobCategory tương ứng
            try:
                job_category = JobCategory.objects.get(name=new_category_name)
                skill.category_new = job_category
                skill.save(update_fields=['category_new'])
            except JobCategory.DoesNotExist:
                print(f"Warning: Không tìm thấy danh mục '{new_category_name}' cho kỹ năng '{skill.name}'")


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_add_address_map_url'),
        ('jobs', '0008_add_location_map_url'),
    ]

    operations = [
        # Bước 1: Đổi tên trường cũ
        migrations.RenameField(
            model_name='skill',
            old_name='category',
            new_name='category_old',
        ),
        
        # Bước 2: Thêm trường mới (ForeignKey)
        migrations.AddField(
            model_name='skill',
            name='category_new',
            field=models.ForeignKey(
                blank=True, 
                null=True,
                help_text='Danh mục kỹ năng', 
                on_delete=django.db.models.deletion.SET_NULL, 
                related_name='skills', 
                to='jobs.jobcategory'
            ),
        ),
        
        # Bước 3: Chuyển dữ liệu
        migrations.RunPython(migrate_category_data, reverse_code=migrations.RunPython.noop),
        
        # Bước 4: Xóa trường cũ
        migrations.RemoveField(
            model_name='skill',
            name='category_old',
        ),
        
        # Bước 5: Đổi tên trường mới thành category
        migrations.RenameField(
            model_name='skill',
            old_name='category_new',
            new_name='category',
        ),
    ]
