from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import UserProfile, Skill, Complaint

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Form đăng ký người dùng với Bootstrap styling"""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    # Giới hạn chỉ cho phép chọn 'employer' hoặc 'worker', không cho phép chọn 'admin'
    USER_TYPE_CHOICES = (
        ('employer', 'Nhà tuyển dụng'),
        ('worker', 'Người tìm việc'),
    )
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 
                 'user_type', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thêm Bootstrap classes cho tất cả fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })
        
        # Custom labels tiếng Việt
        self.fields['username'].label = 'Tên đăng nhập'
        self.fields['email'].label = 'Email'
        self.fields['first_name'].label = 'Họ'
        self.fields['last_name'].label = 'Tên'
        self.fields['phone_number'].label = 'Số điện thoại'
        self.fields['user_type'].label = 'Loại tài khoản'
        self.fields['password1'].label = 'Mật khẩu'
        self.fields['password2'].label = 'Xác nhận mật khẩu'
        
        # Custom widget cho user_type
        self.fields['user_type'].widget.attrs.update({'class': 'form-select'})
        
        # Ghi đè các thông báo lỗi mật khẩu bằng tiếng Việt
        self.fields['password1'].error_messages.update({
            'password_too_short': 'Mật khẩu quá ngắn. Phải có ít nhất 8 ký tự.',
            'password_entirely_numeric': 'Mật khẩu không thể chỉ chứa số.',
        })
        self.fields['password2'].error_messages.update({
            'password_mismatch': 'Hai mật khẩu không khớp nhau.'
        })
        
        # Thêm trợ giúp tiếng Việt cho các trường mật khẩu
        self.fields['password1'].help_text = 'Mật khẩu của bạn phải có ít nhất 8 ký tự và không thể chỉ chứa số.'
        self.fields['password2'].help_text = 'Nhập lại mật khẩu để xác nhận.'
        
        # Thêm trợ giúp cho các trường khác
        self.fields['username'].help_text = 'Tên đăng nhập phải là duy nhất.'
        self.fields['email'].help_text = 'Email phải là duy nhất, mỗi email chỉ được đăng ký 1 tài khoản.'
        self.fields['phone_number'].help_text = 'Mỗi số điện thoại chỉ được đăng ký 1 tài khoản.'
    
    def clean_email(self):
        """Kiểm tra email đã tồn tại chưa"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email này đã được sử dụng. Vui lòng chọn email khác.')
        return email
    
    def clean_phone_number(self):
        """Kiểm tra số điện thoại đã tồn tại chưa"""
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('Số điện thoại này đã được sử dụng. Vui lòng chọn số khác.')
        return phone_number

class CustomAuthenticationForm(AuthenticationForm):
    """Form đăng nhập với Bootstrap styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thêm Bootstrap classes
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Tên đăng nhập'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mật khẩu'
        })
        
        # Custom labels
        self.fields['username'].label = 'Tên đăng nhập'
        self.fields['password'].label = 'Mật khẩu'

class UserProfileForm(forms.ModelForm):
    """Form chỉnh sửa hồ sơ người dùng - tối giản cho casual jobs"""
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'skills', 'custom_skills', 'is_available']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Skills có sẵn - checkbox
        self.fields['skills'].widget = forms.CheckboxSelectMultiple()
        self.fields['skills'].queryset = Skill.objects.filter(is_active=True)
        self.fields['skills'].required = False
        
        # Custom skills - textarea
        self.fields['custom_skills'].widget = forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        self.fields['custom_skills'].required = False
        
        # Thêm Bootstrap classes cho các fields
        for field_name, field in self.fields.items():
            if field_name == 'is_available':
                field.widget.attrs.update({'class': 'form-check-input'})
            elif field_name in ['bio', 'custom_skills']:
                field.widget.attrs.update({
                    'class': 'form-control',
                    'rows': 3
                })
            elif field_name not in ['skills']:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Custom labels tiếng Việt
        self.fields['bio'].label = 'Giới thiệu bản thân'
        self.fields['skills'].label = 'Kỹ năng có sẵn'
        self.fields['custom_skills'].label = 'Kỹ năng khác'
        self.fields['is_available'].label = 'Đang tìm việc'

class AdminComplaintForm(forms.ModelForm):
    """Form xử lý khiếu nại cho admin"""
    
    class Meta:
        model = Complaint
        fields = ['status', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].label = 'Trạng thái'
        self.fields['admin_notes'].label = 'Ghi chú của Admin'

class SkillForm(forms.ModelForm):
    """Form thêm/sửa kỹ năng"""
    
    class Meta:
        model = Skill
        fields = ['name', 'category', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Tên kỹ năng'
        self.fields['category'].label = 'Danh mục'
        self.fields['is_active'].label = 'Kích hoạt'
        
class UserForm(forms.ModelForm):
    """Form cập nhật thông tin cá nhân của người dùng"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'date_of_birth']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = 'Họ'
        self.fields['last_name'].label = 'Tên'
        self.fields['email'].label = 'Email'
        self.fields['phone_number'].label = 'Số điện thoại'
        self.fields['address'].label = 'Địa chỉ'
        self.fields['date_of_birth'].label = 'Ngày sinh'
        
        # Thêm trợ giúp cho các trường
        self.fields['email'].help_text = 'Email phải là duy nhất, mỗi email chỉ được đăng ký 1 tài khoản.'
        self.fields['phone_number'].help_text = 'Mỗi số điện thoại chỉ được đăng ký 1 tài khoản.'
        self.fields['date_of_birth'].help_text = 'Định dạng ngày/tháng/năm.'
        
    def clean_email(self):
        """Kiểm tra email đã tồn tại chưa, trừ email hiện tại của user"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Email này đã được sử dụng. Vui lòng chọn email khác.')
        return email
    
    def clean_phone_number(self):
        """Kiểm tra số điện thoại đã tồn tại chưa, trừ số điện thoại hiện tại của user"""
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and User.objects.filter(phone_number=phone_number).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Số điện thoại này đã được sử dụng. Vui lòng chọn số khác.')
        return phone_number
