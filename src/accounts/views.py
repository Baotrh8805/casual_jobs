from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from .forms import (CustomUserCreationForm, UserProfileForm, AdminComplaintForm, 
                  CustomAuthenticationForm, UserForm, SkillForm)
from .models import UserProfile, Skill, Complaint, AdminActivity, User, Notification
from jobs.models import JobCategory

def is_admin(user):
    """Kiểm tra user có phải admin không"""
    return user.is_authenticated and (user.user_type == 'admin' or user.is_superuser)

class SignUpView(CreateView):
    """View đăng ký người dùng"""
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        """Kiểm tra thêm một lần nữa để đảm bảo không ai đăng ký làm admin"""
        user_type = form.cleaned_data.get('user_type')
        if user_type == 'admin':
            form.add_error('user_type', 'Không thể đăng ký tài khoản quản trị viên')
            return self.form_invalid(form)
            
        # Tiếp tục xử lý nếu không phải admin
        response = super().form_valid(form)
        # Tạo UserProfile cho user mới
        UserProfile.objects.create(user=self.object)
        messages.success(self.request, 'Đăng ký thành công! Vui lòng đăng nhập.')
        return response
    
def login_view(request):
    """Custom login view to show success message"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Xin chào {user.first_name or user.username}! Đăng nhập thành công.')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm(request)
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """Custom logout view that accepts both GET and POST methods"""
    logout(request)
    messages.success(request, 'Đăng xuất thành công. Hẹn gặp lại bạn!')
    return redirect('accounts:login')
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Tạo UserProfile cho user mới
        UserProfile.objects.create(user=self.object)
        messages.success(self.request, 'Đăng ký thành công! Vui lòng đăng nhập.')
        return response

@login_required
def profile_view(request):
    """View hiển thị và chỉnh sửa profile"""
    # Admin không cần profile form, chỉ cần user form
    if request.user.user_type == 'admin':
        if request.method == 'POST':
            user_form = UserForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Cập nhật hồ sơ thành công!')
                return redirect('accounts:profile')
        else:
            user_form = UserForm(instance=request.user)
        
        context = {
            'user_form': user_form,
            'profile_form': None,
            'profile': None,
        }
    else:
        # Worker và Employer cần cả user form và profile form
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            user_form = UserForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(request.POST, instance=profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Cập nhật hồ sơ thành công!')
                return redirect('accounts:profile')
        else:
            user_form = UserForm(instance=request.user)
            profile_form = UserProfileForm(instance=profile)
        
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'profile': profile,
        }
    
    return render(request, 'accounts/profile.html', context)

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Dashboard chính cho admin"""
    # Import JobCategory và JobApplication
    from jobs.models import JobCategory, JobApplication
    
    # Thống kê tổng quan - loại bỏ admin khỏi thống kê
    total_users = User.objects.exclude(user_type='admin').exclude(is_superuser=True).count()
    total_workers = User.objects.filter(user_type='worker').count()
    total_employers = User.objects.filter(user_type='employer').count()
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status='pending').count()
    
    # Thống kê danh mục công việc và đơn ứng tuyển
    total_categories = JobCategory.objects.filter(is_active=True).count()
    total_accepted_applications = JobApplication.objects.filter(status='accepted').count()
    
    # Thống kê theo thời gian (30 ngày qua) - loại bỏ admin
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_users_30d = User.objects.filter(created_at__gte=thirty_days_ago).exclude(user_type='admin').exclude(is_superuser=True).count()
    new_complaints_30d = Complaint.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # Top skills được sử dụng nhiều nhất
    top_skills = Skill.objects.annotate(
        usage_count=Count('userprofile')
    ).order_by('-usage_count')[:10]
    
    # Danh mục công việc với số lượng job posts
    top_categories = JobCategory.objects.filter(is_active=True).annotate(
        job_count=Count('jobs')
    ).order_by('-job_count')[:10]
    
    # Khiếu nại mới nhất
    recent_complaints = Complaint.objects.select_related('user').order_by('-created_at')[:5]
    
    # Hoạt động admin gần đây
    recent_activities = AdminActivity.objects.select_related('admin').order_by('-created_at')[:10]
    
    context = {
        'total_users': total_users,
        'total_workers': total_workers,
        'total_employers': total_employers,
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'total_categories': total_categories,
        'total_accepted_applications': total_accepted_applications,
        'new_users_30d': new_users_30d,
        'new_complaints_30d': new_complaints_30d,
        'top_skills': top_skills,
        'top_categories': top_categories,
        'recent_complaints': recent_complaints,
        'recent_activities': recent_activities,
    }
    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_skills_management(request):
    """Quản lý skills với tìm kiếm"""
    # Lấy tất cả kỹ năng
    skills = Skill.objects.select_related('category').all()
    
    # Lọc theo tìm kiếm
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '').strip()
    status_filter = request.GET.get('status', '')
    
    if search_query:
        skills = skills.filter(
            Q(name__icontains=search_query) | 
            Q(normalized_name__icontains=search_query)
        )
    
    if category_filter:
        # Lọc theo ID của category
        skills = skills.filter(category_id=category_filter)
    
    if status_filter == 'active':
        skills = skills.filter(is_active=True)
    elif status_filter == 'inactive':
        skills = skills.filter(is_active=False)
    
    skills = skills.order_by('name')
    
    # Lấy danh sách các danh mục từ JobCategory
    all_categories = JobCategory.objects.filter(is_active=True).order_by('name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_skill':
            form = SkillForm(request.POST)
            if form.is_valid():
                skill = form.save()
                messages.success(request, f'Đã thêm kỹ năng: {skill.name}')
                # Ghi log hoạt động
                AdminActivity.objects.create(
                    admin=request.user,
                    action='skill_added',
                    description=f'Thêm kỹ năng mới: {skill.name}'
                )
                return redirect('accounts:admin_skills')
            else:
                messages.error(request, 'Có lỗi khi thêm kỹ năng')
        
        elif action == 'toggle_skill':
            skill_id = request.POST.get('skill_id')
            try:
                skill = Skill.objects.get(id=skill_id)
                skill.is_active = not skill.is_active
                skill.save()
                status = 'kích hoạt' if skill.is_active else 'vô hiệu hóa'
                messages.success(request, f'Đã {status} kỹ năng: {skill.name}')
            except Skill.DoesNotExist:
                messages.error(request, 'Kỹ năng không tồn tại')
        
        return redirect('accounts:admin_skills')
    
    # Tạo form mới cho thêm kỹ năng
    form = SkillForm()
    
    context = {
        'skills': skills,
        'all_categories': all_categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'total_skills': skills.count(),
        'form': form,
    }
    return render(request, 'accounts/admin_skills.html', context)

@login_required
@user_passes_test(is_admin)
def admin_categories_management(request):
    """Quản lý danh mục công việc"""
    categories = JobCategory.objects.all().order_by('name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_category':
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            icon = request.POST.get('icon', '').strip()
            color = request.POST.get('color', '#007bff').strip()
            if name:
                category, created = JobCategory.objects.get_or_create(
                    name=name,
                    defaults={
                        'description': description,
                        'icon': icon,
                        'color': color
                    }
                )
                if created:
                    messages.success(request, f'Đã thêm danh mục: {name}')
                    AdminActivity.objects.create(
                        admin=request.user,
                        action='category_added',
                        description=f'Thêm danh mục mới: {name}'
                    )
                else:
                    messages.warning(request, f'Danh mục "{name}" đã tồn tại')
            else:
                messages.error(request, 'Tên danh mục không được để trống')
        
        elif action == 'toggle_category':
            category_id = request.POST.get('category_id')
            try:
                category = JobCategory.objects.get(id=category_id)
                category.is_active = not category.is_active
                category.save()
                status = 'kích hoạt' if category.is_active else 'vô hiệu hóa'
                messages.success(request, f'Đã {status} danh mục: {category.name}')
            except JobCategory.DoesNotExist:
                messages.error(request, 'Danh mục không tồn tại')
        
        elif action == 'edit_category':
            category_id = request.POST.get('category_id')
            try:
                category = JobCategory.objects.get(id=category_id)
                category.name = request.POST.get('name', '').strip()
                category.description = request.POST.get('description', '').strip()
                category.icon = request.POST.get('icon', '').strip()
                category.color = request.POST.get('color', '#007bff').strip()
                category.save()
                messages.success(request, f'Đã cập nhật danh mục: {category.name}')
            except JobCategory.DoesNotExist:
                messages.error(request, 'Danh mục không tồn tại')
        
        return redirect('accounts:admin_categories')
    
    context = {
        'categories': categories,
    }
    return render(request, 'accounts/admin_categories.html', context)

@login_required
@user_passes_test(is_admin)
def admin_complaints(request):
    """Quản lý khiếu nại"""
    status_filter = request.GET.get('status', 'all')
    type_filter = request.GET.get('type', 'all')
    
    complaints = Complaint.objects.select_related('user').all()
    
    if status_filter != 'all':
        complaints = complaints.filter(status=status_filter)
    if type_filter != 'all':
        complaints = complaints.filter(complaint_type=type_filter)
    
    complaints = complaints.order_by('-created_at')
    
    context = {
        'complaints': complaints,
        'status_choices': Complaint.STATUS_CHOICES,
        'type_choices': Complaint.TYPE_CHOICES,
        'current_status': status_filter,
        'current_type': type_filter,
    }
    return render(request, 'accounts/admin_complaints.html', context)

@login_required
@user_passes_test(is_admin)
def admin_complaint_detail(request, complaint_id):
    """Chi tiết khiếu nại"""
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    if request.method == 'POST':
        form = AdminComplaintForm(request.POST, instance=complaint)
        if form.is_valid():
            old_status = complaint.status
            form.save()
            
            # Cập nhật thời gian giải quyết nếu chuyển sang resolved
            if old_status != 'resolved' and complaint.status == 'resolved':
                complaint.resolved_at = timezone.now()
                complaint.save()
            
            # Ghi log hoạt động
            AdminActivity.objects.create(
                admin=request.user,
                action='complaint_resolved',
                description=f'Cập nhật khiếu nại: {complaint.title}',
                target_user=complaint.user
            )
            
            messages.success(request, 'Cập nhật khiếu nại thành công!')
            return redirect('accounts:admin_complaints')
    else:
        form = AdminComplaintForm(instance=complaint)
    
    context = {
        'complaint': complaint,
        'form': form,
    }
    return render(request, 'accounts/admin_complaint_detail.html', context)

@login_required
@user_passes_test(is_admin)
def admin_user_management(request):
    """Quản lý người dùng"""
    user_type_filter = request.GET.get('type', 'all')
    search_query = request.GET.get('search', '')
    
    # Loại bỏ các tài khoản admin khỏi danh sách quản lý
    users = User.objects.exclude(user_type='admin').exclude(is_superuser=True)
    
    if user_type_filter != 'all':
        users = users.filter(user_type=user_type_filter)
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    users = users.order_by('-date_joined')
    
    context = {
        'users': users,
        'user_types': User.USER_TYPES,
        'current_type': user_type_filter,
        'search_query': search_query,
    }
    return render(request, 'accounts/admin_users.html', context)

@login_required
@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    """Chi tiết người dùng"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Kiểm tra không cho phép admin thao tác trên chính tài khoản của mình
        if user.id == request.user.id:
            messages.error(request, 'Bạn không thể thực hiện thao tác này trên chính tài khoản của mình!')
            return redirect('accounts:admin_user_detail', user_id=user_id)
        
        action = request.POST.get('action')
        if action == 'toggle_verification':
            user.is_verified = not user.is_verified
            user.save()
            status = 'xác thực' if user.is_verified else 'hủy xác thực'
            messages.success(request, f'Đã {status} người dùng: {user.username}')
            
            # Ghi log hoạt động
            AdminActivity.objects.create(
                admin=request.user,
                action='user_verified',
                description=f'{status.title()} người dùng: {user.username}',
                target_user=user
            )
        
        elif action == 'toggle_ban':
            user.is_active = not user.is_active
            user.save()
            status = 'cấm' if not user.is_active else 'bỏ cấm'
            messages.success(request, f'Đã {status} người dùng: {user.username}')
            
            # Ghi log hoạt động
            AdminActivity.objects.create(
                admin=request.user,
                action='user_banned',
                description=f'{status.title()} người dùng: {user.username}',
                target_user=user
            )
        
        return redirect('accounts:admin_user_detail', user_id=user_id)
    
    # Lấy thông tin profile nếu có
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = None
    
    # Lấy khiếu nại của user này
    complaints = Complaint.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'target_user': user,
        'profile': profile,
        'complaints': complaints,
    }
    return render(request, 'accounts/admin_user_detail.html', context)

def home_view(request):
    """View trang chủ"""
    from jobs.models import JobPost, JobCategory
    
    # Lấy các job mới nhất, sắp xếp theo ưu tiên (high trước) và thời gian tạo
    from django.db.models import Case, When, IntegerField
    
    recent_jobs = JobPost.objects.filter(status='published').select_related('category').annotate(
        priority_order=Case(
            When(priority='high', then=1),
            When(priority='normal', then=0),
            default=0,
            output_field=IntegerField()
        )
    ).order_by('-priority_order', '-created_at').values(
        'id', 'title', 'description', 'location', 'work_date', 'work_time_start', 'work_time_end',
        'payment_type', 'payment_amount', 'priority', 'created_at', 'category__name'
    )[:6]
    # Lấy các categories
    categories = JobCategory.objects.filter(is_active=True)
    
    context = {
        'recent_jobs': recent_jobs,
        'categories': categories,
    }
    return render(request, 'home.html', context)

def check_username(request):
    """API endpoint để kiểm tra username đã tồn tại chưa"""
    username = request.GET.get('username', '').strip()
    if not username:
        return JsonResponse({'available': False, 'message': 'Username không được để trống'})
    
    if len(username) < 3:
        return JsonResponse({'available': False, 'message': 'Username phải có ít nhất 3 ký tự'})
    
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({
        'available': not exists,
        'message': 'Tên đăng nhập khả dụng' if not exists else 'Tên đăng nhập đã được sử dụng'
    })

def check_email(request):
    """API endpoint để kiểm tra email đã tồn tại chưa"""
    email = request.GET.get('email', '').strip()
    if not email:
        return JsonResponse({'available': False, 'message': 'Email không được để trống'})
    
    exists = User.objects.filter(email=email).exists()
    return JsonResponse({
        'available': not exists,
        'message': 'Email khả dụng' if not exists else 'Email đã được sử dụng'
    })

def check_phone(request):
    """API endpoint để kiểm tra số điện thoại đã tồn tại chưa"""
    phone = request.GET.get('phone', '').strip()
    if not phone:
        return JsonResponse({'available': True, 'message': 'Số điện thoại không bắt buộc'})
    
    exists = User.objects.filter(phone_number=phone).exists()
    return JsonResponse({
        'available': not exists,
        'message': 'Số điện thoại khả dụng' if not exists else 'Số điện thoại đã được sử dụng'
    })

@user_passes_test(is_admin)
def admin_applications(request):
    """
    View cho admin xem tất cả đơn ứng tuyển đã được phê duyệt
    
    Hiển thị:
    - Tất cả JobApplication có status='accepted'
    - Thông tin ứng viên (worker)
    - Thông tin công việc
    - Thông tin nhà tuyển dụng (employer)
    """
    from jobs.models import JobApplication
    
    # Lấy tất cả đơn ứng tuyển đã được chấp nhận
    # Sử dụng select_related để tối ưu query (tránh N+1 problem)
    applications = JobApplication.objects.filter(
        status='accepted'
    ).select_related(
        'applicant',           # Worker info
        'applicant__profile',  # Worker profile
        'job',                 # Job info
        'job__employer',       # Employer info
        'job__category'        # Job category
    ).order_by('-applied_at')
    
    # Lọc theo từ khóa (tìm kiếm)
    keyword = request.GET.get('keyword', '').strip()
    if keyword:
        applications = applications.filter(
            Q(applicant__username__icontains=keyword) |
            Q(applicant__first_name__icontains=keyword) |
            Q(applicant__last_name__icontains=keyword) |
            Q(job__title__icontains=keyword) |
            Q(job__employer__username__icontains=keyword)
        )
    
    # Lọc theo thời gian
    time_filter = request.GET.get('time_filter', '')
    if time_filter:
        today = timezone.now().date()
        if time_filter == 'today':
            applications = applications.filter(applied_at__date=today)
        elif time_filter == 'this_week':
            start_of_week = today - timedelta(days=today.weekday())
            applications = applications.filter(applied_at__date__gte=start_of_week)
        elif time_filter == 'this_month':
            applications = applications.filter(
                applied_at__year=today.year,
                applied_at__month=today.month
            )
    
    # Phân trang
    from django.core.paginator import Paginator
    paginator = Paginator(applications, 20)  # 20 đơn mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'applications': page_obj,
        'total_applications': applications.count(),
        'keyword': keyword,
        'time_filter': time_filter,
    }
    
    return render(request, 'accounts/admin_applications.html', context)

@login_required
def notifications_view(request):
    """Hiển thị danh sách thông báo của người dùng"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Đếm số thông báo chưa đọc
    unread_count = notifications.filter(is_read=False).count()
    
    # Phân trang
    from django.core.paginator import Paginator
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Đánh dấu thông báo đã đọc"""
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    # Redirect đến link nếu có, không thì về trang thông báo
    if notification.link:
        return redirect(notification.link)
    return redirect('accounts:notifications')

@login_required
def mark_all_notifications_read(request):
    """Đánh dấu tất cả thông báo đã đọc"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'Đã đánh dấu tất cả thông báo là đã đọc.')
    return redirect('accounts:notifications')

@login_required
def delete_notification(request, notification_id):
    """Xóa thông báo"""
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.delete()
    messages.success(request, 'Đã xóa thông báo.')
    return redirect('accounts:notifications')

@login_required
def get_unread_notifications_count(request):
    """API trả về số thông báo chưa đọc (dùng cho AJAX)"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})

@login_required
def get_recent_notifications(request):
    """API trả về 5 thông báo mới nhất (dùng cho dropdown)"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    notifications_data = []
    for notif in notifications:
        # Icon theo loại
        if notif.notification_type == 'application_accepted':
            icon = 'bi-check-circle'
            badge_class = 'success'
        elif notif.notification_type == 'application_rejected':
            icon = 'bi-x-circle'
            badge_class = 'danger'
        elif notif.notification_type == 'new_application':
            icon = 'bi-file-earmark-text'
            badge_class = 'info'
        elif notif.notification_type == 'job_full':
            icon = 'bi-people-fill'
            badge_class = 'warning'
        else:
            icon = 'bi-info-circle'
            badge_class = 'secondary'
        
        # Tính thời gian
        from django.utils.timesince import timesince
        time_ago = timesince(notif.created_at) + ' trước'
        
        notifications_data.append({
            'id': notif.id,
            'title': notif.title,
            'message': notif.message[:100] + '...' if len(notif.message) > 100 else notif.message,
            'is_read': notif.is_read,
            'icon': icon,
            'badge_class': badge_class,
            'time_ago': time_ago,
            'link': notif.link or '',
        })
    
    return JsonResponse({'notifications': notifications_data})

@login_required
def get_work_schedule(request):
    """API trả về lịch làm việc của user (các đơn đã được chấp nhận)"""
    from jobs.models import JobApplication
    from datetime import datetime, timedelta
    
    # Lấy tháng và năm từ request, mặc định là tháng hiện tại
    try:
        year = int(request.GET.get('year', datetime.now().year))
        month = int(request.GET.get('month', datetime.now().month))
    except:
        year = datetime.now().year
        month = datetime.now().month
    
    # Lấy các application đã được chấp nhận của user trong tháng này
    from datetime import date
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    applications = JobApplication.objects.filter(
        applicant=request.user,
        status='accepted',
        job__work_date__gte=first_day,
        job__work_date__lte=last_day
    ).select_related('job', 'job__category').order_by('job__work_date')
    
    # Tổ chức dữ liệu theo ngày
    schedule_by_date = {}
    for app in applications:
        work_date = app.job.work_date.strftime('%Y-%m-%d')
        if work_date not in schedule_by_date:
            schedule_by_date[work_date] = []
        
        schedule_by_date[work_date].append({
            'job_id': app.job.id,
            'title': app.job.title,
            'location': app.job.location,
            'time_start': app.job.work_time_start.strftime('%H:%M'),
            'time_end': app.job.work_time_end.strftime('%H:%M'),
            'payment': f"{app.job.payment_amount:,}đ",
            'category': app.job.category.name if app.job.category else 'Khác',
        })
    
    return JsonResponse({'schedule': schedule_by_date})
