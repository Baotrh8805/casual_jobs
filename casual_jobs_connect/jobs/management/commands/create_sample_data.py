from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from jobs.models import JobCategory, JobPost
from accounts.models import UserProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho hệ thống CasualJobs'

    def handle(self, *args, **options):
        self.stdout.write('Bắt đầu tạo dữ liệu mẫu...')
        
        # Tạo Job Categories
        self.create_job_categories()
        
        # Tạo users mẫu
        self.create_sample_users()
        
        # Tạo job posts mẫu
        self.create_sample_jobs()
        
        self.stdout.write(
            self.style.SUCCESS('Hoàn thành tạo dữ liệu mẫu!')
        )

    def create_job_categories(self):
        """Tạo các danh mục công việc mẫu"""
        categories_data = [
            {
                'name': 'Pha chế',
                'description': 'Các công việc liên quan đến pha chế đồ uống tại quán café, trà sữa',
                'icon': 'cup-hot',
                'color': '#8B4513'
            },
            {
                'name': 'Phục vụ bàn',
                'description': 'Phục vụ khách hàng tại nhà hàng, quán ăn, café',
                'icon': 'person-standing',
                'color': '#FF6B6B'
            },
            {
                'name': 'Bảo vệ',
                'description': 'Công việc bảo vệ an ninh tại các tòa nhà, sự kiện',
                'icon': 'shield-check',
                'color': '#4ECDC4'
            },
            {
                'name': 'Lễ tân',
                'description': 'Tiếp đón khách hàng, hỗ trợ thông tin tại các cơ quan, doanh nghiệp',
                'icon': 'person-badge',
                'color': '#45B7D1'
            },
            {
                'name': 'Giao hàng',
                'description': 'Giao hàng hóa, thực phẩm trong khu vực',
                'icon': 'bicycle',
                'color': '#96CEB4'
            },
            {
                'name': 'Bán hàng',
                'description': 'Bán hàng tại cửa hàng, siêu thị, sự kiện',
                'icon': 'shop',
                'color': '#FFEAA7'
            },
            {
                'name': 'Dọn dẹp',
                'description': 'Vệ sinh, dọn dẹp tại văn phòng, nhà ở, sự kiện',
                'icon': 'brush',
                'color': '#DDA0DD'
            },
            {
                'name': 'Hỗ trợ sự kiện',
                'description': 'Hỗ trợ tổ chức các sự kiện, hội thảo, tiệc cưới',
                'icon': 'calendar-event',
                'color': '#FF7675'
            }
        ]
        
        for category_data in categories_data:
            category, created = JobCategory.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data
            )
            if created:
                self.stdout.write(f'✓ Tạo danh mục: {category.name}')

    def create_sample_users(self):
        """Tạo users mẫu"""
        # Tạo admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@casualjobs.com',
                password='admin123',
                first_name='Admin',
                last_name='CasualJobs'
            )
            self.stdout.write('✓ Tạo admin user: admin/admin123')
        
        # Tạo employer users
        employers_data = [
            {
                'username': 'cafe_highland',
                'email': 'hr@highland.com',
                'first_name': 'Highland',
                'last_name': 'Coffee',
                'phone_number': '0901234567'
            },
            {
                'username': 'nha_hang_golden',
                'email': 'tuyen_dung@golden.com',
                'first_name': 'Golden',
                'last_name': 'Restaurant',
                'phone_number': '0907654321'
            },
            {
                'username': 'cty_bao_ve_an_ninh',
                'email': 'hr@security.com',
                'first_name': 'An Ninh',
                'last_name': 'Security',
                'phone_number': '0905555555'
            }
        ]
        
        for emp_data in employers_data:
            if not User.objects.filter(username=emp_data['username']).exists():
                user = User.objects.create_user(
                    username=emp_data['username'],
                    email=emp_data['email'],
                    password='password123',
                    first_name=emp_data['first_name'],
                    last_name=emp_data['last_name'],
                    phone_number=emp_data['phone_number'],
                    user_type='employer'
                )
                UserProfile.objects.create(user=user)
                self.stdout.write(f'✓ Tạo employer: {user.username}')
        
        # Tạo worker users
        workers_data = [
            {
                'username': 'nguyen_van_a',
                'email': 'nguyenvana@email.com',
                'first_name': 'Nguyễn Văn',
                'last_name': 'A',
                'phone_number': '0912345678',
                'skills': 'Pha chế, Phục vụ khách hàng, Tiếng Anh cơ bản',
                'experience_years': 2,
                'hourly_rate': 50000
            },
            {
                'username': 'tran_thi_b',
                'email': 'tranthib@email.com',
                'first_name': 'Trần Thị',
                'last_name': 'B',
                'phone_number': '0987654321',
                'skills': 'Phục vụ bàn, Giao tiếp khách hàng, Làm việc nhóm',
                'experience_years': 1,
                'hourly_rate': 45000
            },
            {
                'username': 'le_minh_c',
                'email': 'leminhc@email.com',
                'first_name': 'Lê Minh',
                'last_name': 'C',
                'phone_number': '0976543210',
                'skills': 'Bảo vệ, Quan sát, Xử lý tình huống',
                'experience_years': 3,
                'hourly_rate': 60000
            }
        ]
        
        for worker_data in workers_data:
            if not User.objects.filter(username=worker_data['username']).exists():
                user = User.objects.create_user(
                    username=worker_data['username'],
                    email=worker_data['email'],
                    password='password123',
                    first_name=worker_data['first_name'],
                    last_name=worker_data['last_name'],
                    phone_number=worker_data['phone_number'],
                    user_type='worker'
                )
                UserProfile.objects.create(
                    user=user,
                    skills=worker_data['skills'],
                    experience_years=worker_data['experience_years'],
                    hourly_rate=worker_data['hourly_rate'],
                    bio=f'Tôi là {user.get_full_name()}, có {worker_data["experience_years"]} năm kinh nghiệm trong lĩnh vực. Mong muốn tìm được công việc phù hợp.'
                )
                self.stdout.write(f'✓ Tạo worker: {user.username}')

    def create_sample_jobs(self):
        """Tạo các job posts mẫu"""
        # Lấy categories và employers
        categories = {cat.name: cat for cat in JobCategory.objects.all()}
        employers = User.objects.filter(user_type='employer')
        
        if not employers.exists():
            self.stdout.write(self.style.WARNING('Không có employer nào để tạo job posts'))
            return
        
        jobs_data = [
            {
                'title': 'Cần thợ pha chế part-time cuối tuần',
                'description': 'Highland Coffee cần tuyển thợ pha chế làm việc cuối tuần. Yêu cầu có kinh nghiệm pha chế cơ bản, thái độ phục vụ tốt, có thể làm ca sáng hoặc chiều.',
                'category': 'Pha chế',
                'location': 'Quận 1, TP.HCM',
                'duration_hours': 8,
                'payment_amount': 55000,
                'required_skills': 'Pha chế cà phê, Espresso, Latte Art cơ bản',
                'experience_required': 1,
                'number_of_workers': 2,
                'priority': 'high',
                'contact_phone': '0901234567'
            },
            {
                'title': 'Phục vụ bàn nhà hàng Golden - ca tối',
                'description': 'Nhà hàng Golden tuyển nhân viên phục vụ bàn ca tối (17h-23h). Không yêu cầu kinh nghiệm, sẽ đào tạo. Ưu tiên ứng viên giao tiếp tốt, năng động.',
                'category': 'Phục vụ bàn',
                'location': 'Quận 3, TP.HCM',
                'duration_hours': 6,
                'payment_amount': 50000,
                'required_skills': 'Giao tiếp khách hàng, Làm việc nhóm',
                'experience_required': 0,
                'number_of_workers': 3,
                'priority': 'normal',
                'contact_phone': '0907654321'
            },
            {
                'title': 'Bảo vệ tòa nhà văn phòng - ca đêm',
                'description': 'Cần bảo vệ làm ca đêm (22h-6h) tại tòa nhà văn phòng. Yêu cầu nam, tuổi từ 25-45, có kinh nghiệm bảo vệ, sức khỏe tốt.',
                'category': 'Bảo vệ',
                'location': 'Quận 7, TP.HCM',
                'duration_hours': 8,
                'payment_amount': 70000,
                'required_skills': 'Bảo vệ, Quan sát, Báo cáo tình hình',
                'experience_required': 2,
                'number_of_workers': 1,
                'priority': 'urgent',
                'contact_phone': '0905555555'
            },
            {
                'title': 'Lễ tân khách sạn - part-time sáng',
                'description': 'Khách sạn 4 sao cần lễ tân làm part-time ca sáng (6h-14h). Yêu cầu ngoại hình khá, giao tiếp tiếng Anh cơ bản, thái độ phục vụ chuyên nghiệp.',
                'category': 'Lễ tân',
                'location': 'Quận 1, TP.HCM',
                'duration_hours': 8,
                'payment_amount': 60000,
                'required_skills': 'Tiếng Anh, Tin học văn phòng, Giao tiếp',
                'experience_required': 1,
                'number_of_workers': 1,
                'priority': 'high',
                'contact_phone': '0909999999'
            },
            {
                'title': 'Giao hàng thực phẩm - flexible time',
                'description': 'Cần shipper giao đồ ăn trong khu vực nội thành. Có xe máy, giờ làm linh hoạt, thanh toán theo đơn hàng. Phù hợp sinh viên làm thêm.',
                'category': 'Giao hàng',
                'location': 'TP.HCM',
                'duration_hours': 4,
                'payment_amount': 15000,
                'payment_type': 'fixed',
                'required_skills': 'Lái xe máy, Định hướng đường, Giao tiếp',
                'experience_required': 0,
                'number_of_workers': 5,
                'priority': 'normal',
                'contact_phone': '0911111111'
            }
        ]
        
        for i, job_data in enumerate(jobs_data):
            category_name = job_data.pop('category')
            category = categories.get(category_name)
            
            if not category:
                continue
            
            # Chọn employer theo thứ tự
            employer = employers[i % len(employers)]
            
            # Tính toán ngày làm việc (trong vòng 7 ngày tới)
            work_date = timezone.now().date() + timedelta(days=(i % 7) + 1)
            application_deadline = timezone.now() + timedelta(days=(i % 5) + 1)
            
            job_data.update({
                'employer': employer,
                'category': category,
                'work_date': work_date,
                'work_time_start': '08:00',
                'work_time_end': '17:00',
                'application_deadline': application_deadline,
                'status': 'published',
                'contact_email': employer.email
            })
            
            if 'payment_type' not in job_data:
                job_data['payment_type'] = 'hourly'
            
            job, created = JobPost.objects.get_or_create(
                title=job_data['title'],
                employer=employer,
                defaults=job_data
            )
            
            if created:
                self.stdout.write(f'✓ Tạo job: {job.title}')
        
        self.stdout.write(f'Tổng số job posts đã tạo: {JobPost.objects.count()}')