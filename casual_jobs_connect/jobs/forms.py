from django import forms
from .models import JobPost, JobApplication, JobCategory

class JobPostForm(forms.ModelForm):
    """Form tạo và chỉnh sửa bài đăng việc làm"""
    
    class Meta:
        model = JobPost
        fields = [
            'title', 'description', 'category', 'location', 
            'work_date', 'work_time_start', 'work_time_end', 'duration_hours',
            'payment_type', 'payment_amount', 'required_skills', 
            'experience_required', 'number_of_workers', 'priority',
            'application_deadline', 'contact_phone', 'contact_email'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Thêm Bootstrap classes
        for field_name, field in self.fields.items():
            if field_name in ['description', 'required_skills']:
                field.widget.attrs.update({
                    'class': 'form-control',
                    'rows': 4
                })
            elif field_name in ['work_date', 'application_deadline']:
                field.widget.attrs.update({
                    'class': 'form-control',
                    'type': 'date'
                })
            elif field_name in ['work_time_start', 'work_time_end']:
                field.widget.attrs.update({
                    'class': 'form-control',
                    'type': 'time'
                })
            elif field_name in ['payment_type', 'category', 'priority']:
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Custom labels tiếng Việt
        self.fields['title'].label = 'Tiêu đề công việc'
        self.fields['description'].label = 'Mô tả chi tiết'
        self.fields['category'].label = 'Danh mục công việc'
        self.fields['location'].label = 'Địa điểm làm việc'
        self.fields['work_date'].label = 'Ngày làm việc'
        self.fields['work_time_start'].label = 'Giờ bắt đầu'
        self.fields['work_time_end'].label = 'Giờ kết thúc'
        self.fields['duration_hours'].label = 'Số giờ làm việc'
        self.fields['payment_type'].label = 'Hình thức trả lương'
        self.fields['payment_amount'].label = 'Mức lương (VND)'
        self.fields['required_skills'].label = 'Kỹ năng yêu cầu'
        self.fields['experience_required'].label = 'Số năm kinh nghiệm'
        self.fields['number_of_workers'].label = 'Số lượng cần tuyển'
        self.fields['priority'].label = 'Độ ưu tiên'
        self.fields['application_deadline'].label = 'Hạn nộp đơn'
        self.fields['contact_phone'].label = 'Số điện thoại liên hệ'
        self.fields['contact_email'].label = 'Email liên hệ'

class JobApplicationForm(forms.ModelForm):
    """Form ứng tuyển việc làm"""
    
    class Meta:
        model = JobApplication
        fields = ['cover_letter', 'proposed_rate']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Thêm Bootstrap classes
        self.fields['cover_letter'].widget.attrs.update({
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Viết thư giới thiệu bản thân và lý do muốn ứng tuyển công việc này...'
        })
        self.fields['proposed_rate'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mức lương bạn mong muốn (VND)'
        })
        
        # Custom labels
        self.fields['cover_letter'].label = 'Thư xin việc'
        self.fields['proposed_rate'].label = 'Mức lương đề xuất (VND)'
        
        # Make cover_letter required
        self.fields['cover_letter'].required = True

class JobSearchForm(forms.Form):
    """Form tìm kiếm việc làm"""
    
    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tìm kiếm theo từ khóa...'
        }),
        label='Từ khóa'
    )
    
    category = forms.ModelChoiceField(
        queryset=JobCategory.objects.filter(is_active=True),
        required=False,
        empty_label="Tất cả danh mục",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Danh mục'
    )
    
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Địa điểm...'
        }),
        label='Địa điểm'
    )
    
    payment_min = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Lương tối thiểu...'
        }),
        label='Lương tối thiểu (VND)'
    )
    
    payment_max = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Lương tối đa...'
        }),
        label='Lương tối đa (VND)'
    )