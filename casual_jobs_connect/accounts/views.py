from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import CustomUserCreationForm, UserProfileForm, AdminComplaintForm
from .models import UserProfile, Skill, Complaint, AdminActivity, User

def is_admin(user):
    """Kiểm tra user có phải admin không"""
    return user.is_authenticated and (user.user_type == 'admin' or user.is_superuser)

class SignUpView(CreateView):
    """View đăng ký người dùng"""
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
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
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật hồ sơ thành công!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Dashboard chính cho admin"""
    # Thống kê tổng quan
    total_users = User.objects.count()
    total_workers = User.objects.filter(user_type='worker').count()
    total_employers = User.objects.filter(user_type='employer').count()
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status='pending').count()
    
    # Thống kê theo thời gian (30 ngày qua)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_users_30d = User.objects.filter(created_at__gte=thirty_days_ago).count()
    new_complaints_30d = Complaint.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # Top skills được sử dụng nhiều nhất
    top_skills = Skill.objects.annotate(
        usage_count=Count('userprofile')
    ).order_by('-usage_count')[:10]
    
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
        'new_users_30d': new_users_30d,
        'new_complaints_30d': new_complaints_30d,
        'top_skills': top_skills,
        'recent_complaints': recent_complaints,
        'recent_activities': recent_activities,
    }
    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_skills_management(request):
    """Quản lý skills"""
    skills = Skill.objects.all().order_by('name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_skill':
            name = request.POST.get('name', '').strip()
            category = request.POST.get('category', '').strip()
            if name:
                skill, created = Skill.objects.get_or_create(
                    name=name,
                    defaults={'category': category}
                )
                if created:
                    messages.success(request, f'Đã thêm kỹ năng: {name}')
                    # Ghi log hoạt động
                    AdminActivity.objects.create(
                        admin=request.user,
                        action='skill_added',
                        description=f'Thêm kỹ năng mới: {name}'
                    )
                else:
                    messages.warning(request, f'Kỹ năng "{name}" đã tồn tại')
            else:
                messages.error(request, 'Tên kỹ năng không được để trống')
        
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
    
    context = {
        'skills': skills,
    }
    return render(request, 'accounts/admin_skills.html', context)

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
    
    users = User.objects.all()
    
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
    
    # Lấy các job mới nhất
    recent_jobs = JobPost.objects.filter(status='published').order_by('-created_at')[:6]
    # Lấy các categories
    categories = JobCategory.objects.filter(is_active=True)
    
    context = {
        'recent_jobs': recent_jobs,
        'categories': categories,
    }
    return render(request, 'home.html', context)
