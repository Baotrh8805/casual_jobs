from django import forms
from .models import JobPost, JobApplication, JobCategory
from django.utils import timezone
import datetime

class JobPostForm(forms.ModelForm):
    """Form tạo và chỉnh sửa bài đăng việc làm"""
    
    class Meta:
        model = JobPost
        fields = [
            'title', 'description', 'category', 'location', 
            'work_date', 'work_time_start', 'work_time_end', 'duration_hours',
            'payment_type', 'payment_amount', 'required_skills', 
            'experience_required', 'number_of_workers', 'priority',
            'contact_phone', 'contact_email'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Tạo lựa chọn ngày từ hôm nay đến 30 ngày sau
        today = timezone.now().date()
        date_choices = [(today + datetime.timedelta(days=i), (today + datetime.timedelta(days=i)).strftime('%d/%m/%Y')) 
                      for i in range(31)]
                      
        # Cấu hình trường work_date để sử dụng dropdown
        self.fields['work_date'] = forms.DateField(
            label='Ngày làm việc',
            widget=forms.Select(choices=date_choices, attrs={'class': 'form-select'}),
            help_text='Chọn ngày làm việc'
        )
        
        # Không còn cần application_deadline nữa
        
        # Tạo lựa chọn giờ (từ 00:00 đến 23:45 với mỗi bước 15 phút)
        time_choices = []
        for hour in range(24):
            for minute in [0, 15, 30, 45]:
                time_obj = datetime.time(hour, minute)
                time_str = time_obj.strftime('%H:%M')
                time_choices.append((time_str, time_str))
        
        # Cấu hình trường work_time_start để sử dụng dropdown
        self.fields['work_time_start'] = forms.CharField(
            label='Giờ bắt đầu',
            widget=forms.Select(choices=time_choices, attrs={'class': 'form-select', 'id': 'id_work_time_start'}),
            help_text='Chọn giờ bắt đầu'
        )
        
        # Cấu hình trường work_time_end để sử dụng dropdown
        self.fields['work_time_end'] = forms.CharField(
            label='Giờ kết thúc',
            widget=forms.Select(choices=time_choices, attrs={'class': 'form-select', 'id': 'id_work_time_end'}),
            help_text='Chọn giờ kết thúc'
        )
        
        # Làm cho trường duration_hours chỉ đọc
        self.fields['duration_hours'].widget.attrs.update({
            'class': 'form-control',
            'readonly': 'readonly',
            'id': 'id_duration_hours'
        })
        
        # Thêm Bootstrap classes
        for field_name, field in self.fields.items():
            if field_name in ['description', 'required_skills']:
                field.widget.attrs.update({
                    'class': 'form-control',
                    'rows': 4
                })
            elif field_name in ['payment_type', 'category', 'priority']:
                field.widget.attrs.update({'class': 'form-select'})
            elif field_name == 'payment_amount':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'step': '1000'  
                })
            elif field_name == 'contact_phone':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Số điện thoại liên hệ của bạn'
                })
            elif field_name == 'contact_email':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Email liên hệ của bạn'
                })
            elif field_name == 'location':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Địa chỉ cụ thể để người tìm việc biết nơi làm việc'
                })
            elif field_name not in ['work_date', 'application_deadline', 'work_time_start', 'work_time_end', 'duration_hours']:  # Đã xử lý ở trên
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean_work_time_start(self):
        """Chuyển đổi giá trị work_time_start từ chuỗi sang đối tượng time"""
        time_str = self.cleaned_data.get('work_time_start')
        if time_str:
            try:
                hour, minute = map(int, time_str.split(':'))
                return datetime.time(hour, minute)
            except (ValueError, TypeError):
                raise forms.ValidationError("Thời gian không hợp lệ. Vui lòng sử dụng định dạng HH:MM.")
        return time_str
    
    def clean_work_time_end(self):
        """Chuyển đổi giá trị work_time_end từ chuỗi sang đối tượng time"""
        time_str = self.cleaned_data.get('work_time_end')
        if time_str:
            try:
                hour, minute = map(int, time_str.split(':'))
                return datetime.time(hour, minute)
            except (ValueError, TypeError):
                raise forms.ValidationError("Thời gian không hợp lệ. Vui lòng sử dụng định dạng HH:MM.")
        return time_str
    
    def clean(self):
        """Kiểm tra và tính toán lại số giờ làm việc"""
        cleaned_data = super().clean()
        
        work_time_start = cleaned_data.get('work_time_start')
        work_time_end = cleaned_data.get('work_time_end')
        
        # Tính toán thời lượng làm việc nếu có cả giờ bắt đầu và giờ kết thúc
        if work_time_start and work_time_end:
            start_minutes = work_time_start.hour * 60 + work_time_start.minute
            end_minutes = work_time_end.hour * 60 + work_time_end.minute
            
            # Xử lý trường hợp giờ kết thúc là ngày hôm sau
            if end_minutes < start_minutes:
                end_minutes += 24 * 60  # Thêm 24 giờ
            
            # Tính số giờ làm việc (với 2 chữ số thập phân)
            duration_hours = round((end_minutes - start_minutes) / 60, 2)
            cleaned_data['duration_hours'] = duration_hours
        
        return cleaned_data
        
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
            'placeholder': 'Mức lương bạn mong muốn (VND)',
            'step': '1000'  # Thay đổi step thành 1000 VND
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
            'placeholder': 'Lương tối thiểu...',
            'step': '1000'  # Thay đổi step thành 1000 VND
        }),
        label='Lương tối thiểu (VND)'
    )
    
    payment_max = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Lương tối đa...',
            'step': '1000'  # Thay đổi step thành 1000 VND
        }),
        label='Lương tối đa (VND)'
    )