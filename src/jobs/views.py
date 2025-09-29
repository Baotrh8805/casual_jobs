from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
import datetime
from .models import JobPost, JobCategory, JobApplication
from .forms import JobPostForm, JobApplicationForm, JobSearchForm

def job_list_view(request):
    """View danh sách việc làm với tìm kiếm và filter"""
    form = JobSearchForm(request.GET)
    jobs = JobPost.objects.filter(status='published').order_by('-created_at')
    
    # Apply filters if form is valid
    if form.is_valid():
        keyword = form.cleaned_data.get('keyword')
        category = form.cleaned_data.get('category')
        location = form.cleaned_data.get('location')
        payment_min = form.cleaned_data.get('payment_min')
        payment_max = form.cleaned_data.get('payment_max')
        
        if keyword:
            jobs = jobs.filter(
                Q(title__icontains=keyword) | 
                Q(description__icontains=keyword) |
                Q(required_skills__icontains=keyword)
            )
        
        if category:
            jobs = jobs.filter(category=category)
            
        if location:
            jobs = jobs.filter(location__icontains=location)
            
        if payment_min:
            jobs = jobs.filter(payment_amount__gte=payment_min)
            
        if payment_max:
            jobs = jobs.filter(payment_amount__lte=payment_max)
    
    # Pagination
    paginator = Paginator(jobs, 12)  # 12 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_jobs': jobs.count(),
    }
    return render(request, 'jobs/job_list.html', context)

def job_detail_view(request, pk):
    """View chi tiết việc làm"""
    job = get_object_or_404(JobPost, pk=pk)
    
    # Kiểm tra nếu công việc đã bắt đầu nhưng vẫn có trạng thái 'published'
    now = timezone.now()
    work_datetime = timezone.make_aware(datetime.datetime.combine(job.work_date, job.work_time_start))
    
    if job.status == 'published' and now >= work_datetime:
        # Cập nhật trạng thái thành 'closed'
        job.status = 'closed'
        job.save(update_fields=['status'])
        messages.info(request, 'Công việc này đã đến giờ bắt đầu và không thể ứng tuyển nữa.')
    
    # Check if user already applied
    user_application = None
    if request.user.is_authenticated and request.user.user_type == 'worker':
        try:
            user_application = JobApplication.objects.get(job=job, applicant=request.user)
        except JobApplication.DoesNotExist:
            pass
    
    context = {
        'job': job,
        'user_application': user_application,
    }
    return render(request, 'jobs/job_detail.html', context)

@login_required
def job_create_view(request):
    """View tạo bài đăng việc làm (chỉ dành cho employer)"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Chỉ nhà tuyển dụng mới có thể đăng việc làm.')
        return redirect('jobs:job_list')
    
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.status = 'published'
            job.save()
            messages.success(request, 'Đăng việc làm thành công!')
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        # Điền sẵn thông tin nhà tuyển dụng (chỉ điền các trường có dữ liệu)
        initial_data = {}
        
        if request.user.phone_number:
            initial_data['contact_phone'] = request.user.phone_number
            
        if request.user.email:
            initial_data['contact_email'] = request.user.email
            
        if request.user.address:
            initial_data['location'] = request.user.address
            
        form = JobPostForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'Đăng việc làm mới'
    }
    return render(request, 'jobs/job_form.html', context)

@login_required
def job_edit_view(request, pk):
    """View chỉnh sửa bài đăng việc làm"""
    job = get_object_or_404(JobPost, pk=pk, employer=request.user)
    
    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            updated_job = form.save(commit=False)
            
            # Kiểm tra nếu job đã đóng hoặc hết hạn, nhưng thời điểm làm việc mới vẫn còn hạn
            # thì tự động mở lại job (chuyển trạng thái về 'published')
            if job.status in ['closed', 'expired']:
                # Tính thời gian làm việc mới
                work_datetime = timezone.make_aware(
                    datetime.datetime.combine(
                        form.cleaned_data['work_date'], 
                        form.cleaned_data['work_time_start']
                    )
                )
                
                # Nếu thời gian làm việc mới vẫn còn hạn (sau thời điểm hiện tại)
                if work_datetime > timezone.now():
                    updated_job.status = 'published'
                    messages.success(
                        request, 
                        'Thời gian làm việc đã được cập nhật và bài đăng đã được mở lại để ứng tuyển!'
                    )
                else:
                    messages.success(request, 'Cập nhật việc làm thành công!')
            else:
                messages.success(request, 'Cập nhật việc làm thành công!')
            
            updated_job.save()
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        # Sử dụng instance để giữ thông tin hiện có của job
        form = JobPostForm(instance=job)
        
        # Nếu thông tin liên hệ trống, điền từ profile người dùng
        if not job.contact_phone and request.user.phone_number:
            form.fields['contact_phone'].initial = request.user.phone_number
        
        if not job.contact_email and request.user.email:
            form.fields['contact_email'].initial = request.user.email
            
        if not job.location and request.user.address:
            form.fields['location'].initial = request.user.address
    
    context = {
        'form': form,
        'job': job,
        'title': 'Chỉnh sửa việc làm'
    }
    return render(request, 'jobs/job_form.html', context)

@login_required
def my_jobs_view(request):
    """View danh sách việc làm đã đăng (dành cho employer) với bộ lọc"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('jobs:job_list')
    
    # Lấy tất cả công việc của người dùng
    jobs = JobPost.objects.filter(employer=request.user)
    
    # Khởi tạo form lọc
    from .forms import JobFilterForm
    form = JobFilterForm(request.GET)
    
    # Áp dụng các bộ lọc nếu form hợp lệ
    if form.is_valid():
        # Lọc theo từ khóa
        keyword = form.cleaned_data.get('keyword')
        if keyword:
            jobs = jobs.filter(
                Q(title__icontains=keyword) | 
                Q(description__icontains=keyword)
            )
        
        # Lọc theo trạng thái
        status = form.cleaned_data.get('status')
        if status:
            jobs = jobs.filter(status=status)
        
        # Lọc theo danh mục
        category = form.cleaned_data.get('category')
        if category:
            jobs = jobs.filter(category=category)
        
        # Lọc theo thời gian
        time_filter = form.cleaned_data.get('time_filter')
        today = timezone.now().date()
        
        if time_filter == 'upcoming':
            jobs = jobs.filter(work_date__gte=today)
        elif time_filter == 'past':
            jobs = jobs.filter(work_date__lt=today)
        elif time_filter == 'today':
            jobs = jobs.filter(work_date=today)
        elif time_filter == 'this_week':
            start_of_week = today - datetime.timedelta(days=today.weekday())
            end_of_week = start_of_week + datetime.timedelta(days=6)
            jobs = jobs.filter(work_date__gte=start_of_week, work_date__lte=end_of_week)
        elif time_filter == 'this_month':
            jobs = jobs.filter(work_date__year=today.year, work_date__month=today.month)
        
        # Lọc theo có/không có ứng viên
        has_applicants = form.cleaned_data.get('has_applicants')
        if has_applicants == 'yes':
            jobs = jobs.annotate(app_count=Count('applications')).filter(app_count__gt=0)
        elif has_applicants == 'no':
            jobs = jobs.annotate(app_count=Count('applications')).filter(app_count=0)
    
    # Sắp xếp kết quả dựa trên tham số sort
    sort_param = request.GET.get('sort', 'newest')
    
    if sort_param == 'oldest':
        jobs = jobs.order_by('created_at')
    elif sort_param == 'most_applicants':
        jobs = jobs.annotate(app_count=Count('applications')).order_by('-app_count')
    elif sort_param == 'date_asc':
        jobs = jobs.order_by('work_date', 'work_time_start')
    elif sort_param == 'date_desc':
        jobs = jobs.order_by('-work_date', '-work_time_start')
    else:  # Default: newest
        jobs = jobs.order_by('-created_at')
    
    # Phân trang
    paginator = Paginator(jobs, 10)  # 10 công việc mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'jobs': page_obj,
        'filter_form': form,
        'total_jobs': jobs.count(),
    }
    return render(request, 'jobs/my_jobs.html', context)

@login_required
def job_apply_view(request, pk):
    """View ứng tuyển việc làm"""
    job = get_object_or_404(JobPost, pk=pk, status='published')
    
    if request.user.user_type != 'worker':
        messages.error(request, 'Chỉ người tìm việc mới có thể ứng tuyển.')
        return redirect('jobs:job_detail', pk=pk)
    
    # Kiểm tra xem đã đến giờ làm việc chưa
    now = timezone.now()
    work_datetime = timezone.make_aware(datetime.datetime.combine(job.work_date, job.work_time_start))
    
    if now >= work_datetime:
        messages.error(request, 'Công việc này đã bắt đầu và không thể ứng tuyển nữa.')
        return redirect('jobs:job_detail', pk=pk)
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'Bạn đã ứng tuyển công việc này rồi.')
        return redirect('jobs:job_detail', pk=pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            # Sử dụng mức lương từ công việc, không cho phép đề xuất lương
            application.proposed_rate = None
            application.save()
            messages.success(request, 'Ứng tuyển thành công! Nhà tuyển dụng sẽ xem xét đơn của bạn.')
            return redirect('jobs:job_detail', pk=pk)
    else:
        form = JobApplicationForm()
    
    context = {
        'form': form,
        'job': job,
    }
    return render(request, 'jobs/job_apply.html', context)

@login_required
def my_applications_view(request):
    """View danh sách đơn ứng tuyển (dành cho worker)"""
    if request.user.user_type != 'worker':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('jobs:job_list')
    
    applications = JobApplication.objects.filter(
        applicant=request.user
    ).order_by('-applied_at')
    
    context = {
        'applications': applications,
    }
    return render(request, 'jobs/my_applications.html', context)

@login_required
def accept_application_view(request, pk):
    """View chấp nhận đơn ứng tuyển"""
    application = get_object_or_404(
        JobApplication, 
        pk=pk, 
        job__employer=request.user
    )
    
    application.status = 'accepted'
    application.save()
    messages.success(request, f'Đã chấp nhận đơn ứng tuyển của {application.applicant.get_full_name()}.')
    return redirect('jobs:job_detail', pk=application.job.pk)

@login_required
def reject_application_view(request, pk):
    """View từ chối đơn ứng tuyển"""
    application = get_object_or_404(
        JobApplication, 
        pk=pk, 
        job__employer=request.user
    )
    
    application.status = 'rejected'
    application.save()
    messages.success(request, f'Đã từ chối đơn ứng tuyển của {application.applicant.get_full_name()}.')
    return redirect('jobs:job_detail', pk=application.job.pk)
