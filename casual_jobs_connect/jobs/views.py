from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
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
    job = get_object_or_404(JobPost, pk=pk, status='published')
    
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
        form = JobPostForm()
    
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
            form.save()
            messages.success(request, 'Cập nhật việc làm thành công!')
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobPostForm(instance=job)
    
    context = {
        'form': form,
        'job': job,
        'title': 'Chỉnh sửa việc làm'
    }
    return render(request, 'jobs/job_form.html', context)

@login_required
def my_jobs_view(request):
    """View danh sách việc làm đã đăng (dành cho employer)"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('jobs:job_list')
    
    jobs = JobPost.objects.filter(employer=request.user).order_by('-created_at')
    
    context = {
        'jobs': jobs,
    }
    return render(request, 'jobs/my_jobs.html', context)

@login_required
def job_apply_view(request, pk):
    """View ứng tuyển việc làm"""
    job = get_object_or_404(JobPost, pk=pk, status='published')
    
    if request.user.user_type != 'worker':
        messages.error(request, 'Chỉ người tìm việc mới có thể ứng tuyển.')
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
