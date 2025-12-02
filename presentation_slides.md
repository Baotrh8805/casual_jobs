# CasualJobs Connect - Presentation Slides

## Slide 1: Title Slide
**CasualJobs Connect**
*Nền tảng kết nối việc làm bán thời gian*

- Người thực hiện: [Tên của bạn]
- Ngày: 15/10/2025
- Dự án: Hệ thống quản lý việc làm casual

---

## Slide 2: Giới thiệu dự án
### Vấn đề cần giải quyết
- Khó khăn trong việc tìm kiếm công việc bán thời gian
- Thiếu nền tảng tin cậy kết nối người lao động và nhà tuyển dụng
- Cần hệ thống xác thực và ưu tiên công việc

### Mục tiêu
- Tạo nền tảng kết nối hiệu quả
- Xây dựng hệ thống xác thực người dùng
- Cung cấp tính năng ưu tiên công việc

---

## Slide 3: Tính năng chính
### 🔐 Hệ thống xác thực người dùng
- Xác thực tài khoản qua admin
- Phân quyền người dùng (Worker/Employer/Admin)
- Hệ thống đánh giá và complaint

### 👑 Hệ thống ưu tiên công việc
- **Normal Priority**: Miễn phí cho tất cả người dùng
- **High Priority**: Chỉ dành cho tài khoản đã xác thực
- Hiển thị với icon phân biệt (👑 cho high priority)

### 🗺️ Tích hợp Google Maps
- Tự động tạo link Google Maps từ địa chỉ
- Dễ dàng tìm đường đến nơi làm việc
- Lưu trữ link map cho từng công việc

---

## Slide 4: Kiến trúc hệ thống
### Backend
```
Django 5.2.6 + Python 3.13
├── accounts/     # Quản lý người dùng
├── jobs/         # Quản lý công việc
└── templates/    # Giao diện người dùng
```

### Database Models
- **User**: Custom user với xác thực
- **JobPost**: Công việc với priority system
- **JobApplication**: Đơn ứng tuyển
- **Skill**: Kỹ năng người dùng

### Frontend
- Bootstrap 5 responsive design
- JavaScript cho UX enhancement
- Google Maps integration

---

## Slide 5: Database Schema
### Core Models
```python
# User Model (accounts/models.py)
class User(AbstractUser):
    user_type = models.CharField(choices=USER_TYPE_CHOICES)
    is_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15)
    address_map_url = models.URLField(blank=True)

# JobPost Model (jobs/models.py) 
class JobPost(models.Model):
    priority = models.CharField(choices=PRIORITY_CHOICES)
    location_map_url = models.URLField(blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_hours = models.IntegerField()
```

---

## Slide 6: Tính năng Priority System
### Logic Implementation
```python
# Chỉ user đã xác thực mới tạo được high priority job
if form.cleaned_data.get('priority') == 'high':
    if not request.user.is_verified:
        form.add_error('priority', 
            'Chỉ tài khoản đã xác thực mới có thể tạo job ưu tiên cao')
```

### Display Logic
```python
# Sắp xếp job theo priority với SQL Case/When
jobs = JobPost.objects.annotate(
    priority_order=Case(
        When(priority='high', then=1),
        When(priority='normal', then=0),
        output_field=IntegerField()
    )
).order_by('-priority_order', '-created_at')
```

---

## Slide 7: Google Maps Integration
### Auto-generate Map Links
```javascript
// Tự động tạo Google Maps link từ địa chỉ
function generateMapUrl() {
    const address = document.getElementById('id_location').value;
    if (address.trim()) {
        const mapUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
        document.getElementById('id_location_map_url').value = mapUrl;
    }
}
```

### Database Storage
- Lưu trữ link Google Maps cho mỗi job
- Hiển thị button "Xem bản đồ" trong job detail
- User có thể chỉnh sửa link map nếu cần

---

## Slide 8: UI/UX Improvements
### Form Enhancement
- **Combined Time Fields**: Start time và end time trên cùng 1 dòng
- **Priority Dropdown**: Icon 👑 cho high priority
- **Auto-validation**: JavaScript validation real-time

### Responsive Design
```css
/* Bootstrap responsive layout */
<div class="row">
    <div class="col-md-6">
        <label>Giờ bắt đầu</label>
        <input type="time" class="form-control">
    </div>
    <div class="col-md-6">
        <label>Giờ kết thúc</label>
        <input type="time" class="form-control">
    </div>
</div>
```

---

## Slide 9: Security & Validation
### User Verification System
- Admin xác thực thủ công
- Chỉ verified user tạo được high priority job
- Hệ thống complaint và feedback

### Form Validation
```python
class JobPostForm(forms.ModelForm):
    def clean_priority(self):
        priority = self.cleaned_data.get('priority')
        if priority == 'high' and not self.user.is_verified:
            raise ValidationError('Cần xác thực tài khoản')
        return priority
```

---

## Slide 10: Database Migrations
### Migration History
```bash
# Created migrations
0001_initial.py                    # Base models
0002_skill_userprofile_...        # Skills system  
0003_user_is_verified_...         # Verification system
0004_alter_user_email_...         # Field updates

# Jobs migrations
0001_initial.py                    # JobPost model
0002_alter_jobapplication_...     # Application updates
```

### Sample Data Creation
- 20+ sample jobs với mix priority levels
- Test users (verified và unverified)
- Realistic job data với địa chỉ Việt Nam

---

## Slide 11: Testing & Quality Assurance
### Manual Testing Performed
✅ **Priority System**
- Unverified user không thể tạo high priority job
- High priority jobs hiển thị đầu tiên
- Priority sorting hoạt động đúng

✅ **Google Maps Integration**  
- Auto-generate map links từ địa chỉ
- Map buttons hoạt động trong job detail
- Responsive trên mobile

✅ **UI Consistency**
- Homepage và job listing có cùng style
- Priority badges hiển thị consistent
- Form layout responsive

---

## Slide 12: Performance Optimization
### Database Queries
```python
# Optimized job listing với annotation
jobs = JobPost.objects.select_related('posted_by') \
    .filter(status='published') \
    .annotate(priority_order=Case(...)) \
    .order_by('-priority_order', '-created_at')
```

### Frontend Optimization
- Lazy loading cho job images
- Efficient JavaScript event handling
- Minimal CSS/JS bundles

### Caching Strategy
- Template fragment caching cho job lists
- Static file caching
- Database query optimization

---

## Slide 13: Demo Live
### Demo Scenarios
1. **Tạo job với unverified account**
   - Chỉ có thể chọn normal priority
   - High priority bị disable

2. **Tạo job với verified account** 
   - Có thể chọn high priority
   - Job xuất hiện đầu tiên trong list

3. **Google Maps Integration**
   - Nhập địa chỉ → auto-generate map link
   - Click "Xem bản đồ" → mở Google Maps

4. **Responsive Design**
   - Test trên desktop, tablet, mobile
   - Form layout adapt theo screen size

---

## Slide 14: Challenges & Solutions
### Technical Challenges
🔴 **Problem**: Priority sorting không hoạt động với string comparison
✅ **Solution**: Sử dụng Django Case/When annotation

🔴 **Problem**: Template syntax errors với complex logic  
✅ **Solution**: Move logic to views, simplify templates

🔴 **Problem**: UI inconsistency giữa pages
✅ **Solution**: Create reusable template components

### Learning Outcomes
- Django ORM advanced queries
- JavaScript form validation
- Bootstrap responsive design
- Database migration management

---

## Slide 15: Future Enhancements
### Phase 2 Features
🚀 **Payment Integration**
- Stripe/PayPal integration cho high priority jobs
- Automated billing system
- Payment history tracking

🚀 **Real-time Notifications** 
- WebSocket cho instant notifications
- Email notifications
- Mobile push notifications

🚀 **Advanced Search**
- Location-based filtering
- Skill matching algorithm
- Salary range filtering

🚀 **Mobile App**
- React Native mobile app
- GPS location services
- Offline job browsing

---

## Slide 16: Conclusion & Q&A
### Project Summary
✅ **Completed**: Full-featured job platform với priority system
✅ **Technologies**: Django, Bootstrap, JavaScript, SQLite
✅ **Features**: User verification, Google Maps, responsive UI
✅ **Quality**: Tested, optimized, production-ready

### Key Achievements
- 🎯 Giải quyết bài toán kết nối việc làm casual
- 🔐 Xây dựng hệ thống xác thực tin cậy  
- 👑 Tạo tính năng ưu tiên độc đáo
- 🗺️ Tích hợp Google Maps seamlessly

### Questions & Discussion
*Cảm ơn mọi người đã theo dõi!*
*Có câu hỏi gì về dự án không ạ?*

---

## Demo URLs & Test Accounts
### Local Development
- **URL**: http://localhost:8000
- **Admin**: http://localhost:8000/admin

### Test Accounts
```
# Verified User (có thể tạo high priority job)
Username: employer_verified  
Password: test123456

# Unverified User (chỉ tạo được normal priority)  
Username: worker_test
Password: test123456

# Admin Account
Username: admin
Password: admin123
```

### Sample Data
- 20+ jobs với mix priority levels
- Địa chỉ thực tại Việt Nam với Google Maps links
- Đa dạng loại công việc (part-time, freelance, etc.)