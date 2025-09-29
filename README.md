# Casual Jobs Connect

Một ứng dụng web dựa trên Django để kết nối người tìm việc và nhà tuyển dụng trong lĩnh vực công việc bán thời gian/thời vụ.

## Cấu trúc dự án

```
casual/
├── .git/                # Thư mục Git
├── .gitignore           # Các file/thư mục loại trừ khỏi Git
├── README.md            # File này
├── src/                 # Mã nguồn chính của ứng dụng
│   ├── accounts/        # Ứng dụng quản lý người dùng
│   ├── casual_jobs_connect/  # Cấu hình chính của dự án
│   ├── jobs/            # Ứng dụng quản lý công việc
│   ├── templates/       # Templates HTML
│   ├── manage.py        # Script quản lý Django
│   └── dbpython.sqlite3 # Cơ sở dữ liệu SQLite
└── venv/                # Môi trường ảo Python (không bao gồm trong Git)
```

## Cài đặt

1. Clone repository
2. Tạo và kích hoạt môi trường ảo:
   ```bash
   cd casual
   python -m venv venv
   source venv/bin/activate  # Trên Unix/MacOS
   venv\\Scripts\\activate  # Trên Windows
   ```
3. Cài đặt các dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Di chuyển vào thư mục src và chạy server:
   ```bash
   cd src
   python manage.py runserver
   ```

## Tài khoản mẫu

### Admin
- Username: admin
- Password: admin123

### Nhà tuyển dụng
- Username: cafe_highland | Password: password123
- Username: nha_hang_golden | Password: password123
- Username: cty_bao_ve_an_ninh | Password: password123

### Người tìm việc
- Username: nguyen_van_a | Password: password123
- Username: tran_thi_b | Password: password123
- Username: le_minh_c | Password: password123