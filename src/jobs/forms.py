from django import forms
from .models import JobPost, JobApplication, JobCategory
from django.utils import timezone
import datetime

class JobPostForm(forms.ModelForm):
    """Form tạo và chỉnh sửa bài đăng việc làm"""
    
    class Meta:
        model = JobPost
        fields = [
            'title', 'description', 'category', 'location', 'location_map_url',
            'work_date', 'work_time_start', 'work_time_end', 'duration_hours',
            'payment_type', 'payment_amount', 'required_skills', 
            'number_of_workers', 'priority',
            'contact_phone', 'contact_email'
        ]
        # Exclude experience_required field
    
    def __init__(self, *args, **kwargs):
        # Lấy user từ kwargs nếu có
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Cấu hình trường work_date để sử dụng datepicker
        self.fields['work_date'].widget = forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'id_work_date'
        })
        self.fields['work_date'].label = 'Ngày làm việc'
        
        # Tạo lựa chọn giờ và phút riêng biệt
        hour_choices = [(str(i).zfill(2), str(i).zfill(2)) for i in range(24)]
        minute_choices = [('00', '00'), ('15', '15'), ('30', '30'), ('45', '45')]
        
        # Tạo các trường tạm thời cho giờ bắt đầu
        self.fields['work_time_start_hour'] = forms.ChoiceField(
            label='Giờ',
            choices=hour_choices,
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_work_time_start_hour'}),
        )
        
        self.fields['work_time_start_minute'] = forms.ChoiceField(
            label='Phút',
            choices=minute_choices,
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_work_time_start_minute'}),
        )
        
        # Tạo các trường tạm thời cho giờ kết thúc
        self.fields['work_time_end_hour'] = forms.ChoiceField(
            label='Giờ',
            choices=hour_choices,
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_work_time_end_hour'}),
        )
        
        self.fields['work_time_end_minute'] = forms.ChoiceField(
            label='Phút',
            choices=minute_choices,
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_work_time_end_minute'}),
        )
        
        # Giữ các trường ẩn cho giá trị thực
        self.fields['work_time_start_str'] = forms.CharField(
            widget=forms.HiddenInput(attrs={'id': 'id_work_time_start_str'}),
            required=False
        )
        
        self.fields['work_time_end_str'] = forms.CharField(
            widget=forms.HiddenInput(attrs={'id': 'id_work_time_end_str'}),
            required=False
        )
        
        # Nếu đang chỉnh sửa (có instance), lấy giá trị đã lưu
        if self.instance and self.instance.pk:
            if self.instance.work_time_start:
                self.initial['work_time_start_hour'] = self.instance.work_time_start.strftime('%H')
                # Đảm bảo phút được chọn trong các giá trị có sẵn (0, 15, 30, 45)
                minute = int(self.instance.work_time_start.strftime('%M'))
                adjusted_minute = round(minute / 15) * 15
                if adjusted_minute == 60:
                    adjusted_minute = 0
                self.initial['work_time_start_minute'] = str(adjusted_minute).zfill(2)
                
            if self.instance.work_time_end:
                self.initial['work_time_end_hour'] = self.instance.work_time_end.strftime('%H')
                # Đảm bảo phút được chọn trong các giá trị có sẵn (0, 15, 30, 45)
                minute = int(self.instance.work_time_end.strftime('%M'))
                adjusted_minute = round(minute / 15) * 15
                if adjusted_minute == 60:
                    adjusted_minute = 0
                self.initial['work_time_end_minute'] = str(adjusted_minute).zfill(2)
                
        # Ẩn các trường gốc và sử dụng các trường tạm thời thay thế
        self.fields['work_time_start'].widget = forms.HiddenInput()
        self.fields['work_time_end'].widget = forms.HiddenInput()
        
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
            elif field_name == 'location_map_url':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'https://maps.google.com/... (tùy chọn)'
                })
            elif field_name not in ['work_date', 'application_deadline', 'work_time_start', 'work_time_end', 'duration_hours']:  # Đã xử lý ở trên
                field.widget.attrs.update({'class': 'form-control'})

        # Custom labels tiếng Việt
        self.fields['title'].label = 'Tiêu đề công việc'
        self.fields['description'].label = 'Mô tả chi tiết'
        self.fields['category'].label = 'Danh mục công việc'
        self.fields['location'].label = 'Địa điểm làm việc'
        self.fields['location_map_url'].label = 'Link Google Maps'
        self.fields['location_map_url'].help_text = 'Link Google Maps để người tìm việc dễ tìm đường (tùy chọn)'
        self.fields['work_date'].label = 'Ngày làm việc'
        self.fields['work_time_start'].label = 'Giờ bắt đầu'
        self.fields['work_time_end'].label = 'Giờ kết thúc'
        self.fields['duration_hours'].label = 'Số giờ làm việc'
        self.fields['payment_type'].label = 'Hình thức trả lương'
        self.fields['payment_amount'].label = 'Mức lương (VND)'
        self.fields['payment_amount'].help_text = 'Theo giờ: nhập lương/giờ. Theo ca: nhập lương cố định cho cả ngày làm việc'
        self.fields['required_skills'].label = 'Kỹ năng yêu cầu'
        self.fields['number_of_workers'].label = 'Số lượng cần tuyển'
        self.fields['priority'].label = 'Độ ưu tiên'
        
        # Hạn chế mức độ ưu tiên dựa trên trạng thái xác thực của user
        if self.user and not self.user.is_verified:
            # Tài khoản chưa xác thực chỉ được chọn "Bình thường"
            self.fields['priority'].choices = [('normal', 'Bình thường')]
            self.fields['priority'].initial = 'normal'
            self.fields['priority'].help_text = 'Tài khoản chưa xác thực chỉ có thể đặt mức độ ưu tiên "Bình thường". Hãy xác thực tài khoản để sử dụng mức ưu tiên "Cao".'
        else:
            # Tài khoản đã xác thực có thể chọn tất cả mức độ ưu tiên
            self.fields['priority'].help_text = 'Chọn mức độ ưu tiên: Bình thường hoặc Cao'
        
        self.fields['contact_phone'].label = 'Số điện thoại liên hệ'
        self.fields['contact_email'].label = 'Email liên hệ'
    
    def clean_work_time_start(self):
        """Không xử lý ở đây nữa vì đã xử lý trong clean"""
        return self.cleaned_data.get('work_time_start')
    
    def clean_work_time_end(self):
        """Không xử lý ở đây nữa vì đã xử lý trong clean"""
        return self.cleaned_data.get('work_time_end')
    
    def clean(self):
        """Kiểm tra và tính toán lại số giờ làm việc"""
        cleaned_data = super().clean()
        
        # Lấy giá trị từ các trường giờ và phút
        start_hour = cleaned_data.get('work_time_start_hour')
        start_minute = cleaned_data.get('work_time_start_minute')
        end_hour = cleaned_data.get('work_time_end_hour')
        end_minute = cleaned_data.get('work_time_end_minute')
        
        # Kiểm tra xem các trường có giá trị không
        if not start_hour or not start_minute or not end_hour or not end_minute:
            self.add_error(None, "Vui lòng chọn giờ bắt đầu và giờ kết thúc")
            return cleaned_data
            
        # Tạo chuỗi thời gian và lưu vào các trường ẩn
        if start_hour and start_minute:
            cleaned_data['work_time_start_str'] = f"{start_hour}:{start_minute}"
        
        if end_hour and end_minute:
            cleaned_data['work_time_end_str'] = f"{end_hour}:{end_minute}"
        
        # Chuyển đổi thành đối tượng time
        try:
            if start_hour and start_minute:
                work_time_start = datetime.time(int(start_hour), int(start_minute))
                cleaned_data['work_time_start'] = work_time_start
        except (ValueError, TypeError):
            self.add_error('work_time_start_hour', "Giờ bắt đầu không hợp lệ.")
                
        try:
            if end_hour and end_minute:
                work_time_end = datetime.time(int(end_hour), int(end_minute))
                cleaned_data['work_time_end'] = work_time_end
        except (ValueError, TypeError):
            self.add_error('work_time_end_hour', "Giờ kết thúc không hợp lệ.")
                
        # Tính toán thời lượng làm việc nếu có cả giờ bắt đầu và giờ kết thúc
        work_time_start = cleaned_data.get('work_time_start')
        work_time_end = cleaned_data.get('work_time_end')
        
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
    
    def clean_work_date(self):
        """Validate ngày làm việc phải từ hôm nay trở đi"""
        work_date = self.cleaned_data.get('work_date')
        
        if work_date:
            today = timezone.now().date()
            if work_date < today:
                raise forms.ValidationError(
                    'Ngày làm việc phải từ hôm nay trở đi. Vui lòng chọn ngày hợp lệ.'
                )
        
        return work_date
    
    def clean_priority(self):
        """Validate mức độ ưu tiên dựa trên trạng thái xác thực của user"""
        priority = self.cleaned_data.get('priority')
        
        # Nếu user chưa xác thực nhưng cố gắng đặt priority khác 'normal'
        if self.user and not self.user.is_verified and priority != 'normal':
            raise forms.ValidationError(
                'Tài khoản chưa xác thực chỉ có thể đặt mức độ ưu tiên "Bình thường". '
                'Vui lòng xác thực tài khoản để sử dụng mức ưu tiên "Cao".'
            )
        
        return priority

class JobApplicationForm(forms.ModelForm):
    """Form ứng tuyển việc làm"""
    
    class Meta:
        model = JobApplication
        fields = ['cover_letter']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Thêm Bootstrap classes
        self.fields['cover_letter'].widget.attrs.update({
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Viết thư giới thiệu bản thân và lý do muốn ứng tuyển công việc này...'
        })
        
        # Custom labels
        self.fields['cover_letter'].label = 'Thư xin việc'
        
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
    
class JobFilterForm(forms.Form):
    """Form lọc công việc trong trang quản lý"""
    
    STATUS_CHOICES = [
        ('', 'Tất cả trạng thái'),
        ('published', 'Đang đăng'),
        ('expired', 'Hết hạn'),
    ]
    
    TIME_FILTER_CHOICES = [
        ('', 'Tất cả thời gian'),
        ('upcoming', 'Sắp diễn ra'),
        ('past', 'Đã qua'),
        ('today', 'Hôm nay'),
        ('this_week', 'Tuần này'),
        ('this_month', 'Tháng này'),
    ]
    
    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tên công việc...'
        }),
        label='Tìm kiếm'
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Trạng thái'
    )
    
    category = forms.ModelChoiceField(
        queryset=JobCategory.objects.filter(is_active=True),
        required=False,
        empty_label="Tất cả danh mục",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Danh mục'
    )
    
    time_filter = forms.ChoiceField(
        choices=TIME_FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Thời gian'
    )
    
    has_applicants = forms.ChoiceField(
        choices=[
            ('', 'Tất cả'),
            ('yes', 'Có ứng viên'),
            ('no', 'Chưa có ứng viên'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Ứng viên'
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