from django.core.management.base import BaseCommand
from accounts.models import Skill

class Command(BaseCommand):
    help = 'Tạo dữ liệu skills mẫu'

    def handle(self, *args, **options):
        skills_data = [
            ('Pha chế', 'F&B'),
            ('Phục vụ bàn', 'F&B'),
            ('Nấu ăn', 'F&B'),
            ('Thu ngân', 'Bán hàng'),
            ('Bán hàng', 'Bán hàng'),
            ('Giao hàng', 'Vận chuyển'),
            ('Bảo vệ', 'An ninh'),
            ('Lễ tân', 'Văn phòng'),
            ('Dọn dẹp', 'Vệ sinh'),
            ('Tiếng Anh', 'Ngôn ngữ'),
            ('Tiếng Nhật', 'Ngôn ngữ'),
            ('Tiếng Hàn', 'Ngôn ngữ'),
            ('Tin học văn phòng', 'Công nghệ'),
            ('Excel', 'Công nghệ'),
            ('Word', 'Công nghệ'),
            ('PowerPoint', 'Công nghệ'),
            ('Photoshop', 'Công nghệ'),
            ('Lái xe', 'Vận chuyển'),
            ('Sửa chữa', 'Kỹ thuật'),
            ('Lắp ráp', 'Kỹ thuật'),
        ]
        
        created_count = 0
        for skill_name, category in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_name,
                defaults={'category': category}
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created skill: {skill_name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} skills!')
        )
