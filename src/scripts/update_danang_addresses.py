#!/usr/bin/env python
"""
Script cập nhật tất cả địa chỉ về khu vực Đà Nẵng với tọa độ GPS
"""
import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'casual_jobs_connect.settings')
django.setup()

from accounts.models import User
from jobs.models import JobPost

# Các địa chỉ mẫu ở Đà Nẵng với tọa độ GPS thực
DANANG_LOCATIONS = [
    # Quận Hải Châu
    {"address": "123 Trần Phú, Hải Châu, Đà Nẵng", "lat": 16.0544, "lng": 108.2022},
    {"address": "45 Bạch Đằng, Hải Châu, Đà Nẵng", "lat": 16.0611, "lng": 108.2250},
    {"address": "78 Lê Duẩn, Hải Châu, Đà Nẵng", "lat": 16.0678, "lng": 108.2208},
    {"address": "234 Nguyễn Văn Linh, Hải Châu, Đà Nẵng", "lat": 16.0528, "lng": 108.2172},
    {"address": "56 Điện Biên Phủ, Hải Châu, Đà Nẵng", "lat": 16.0694, "lng": 108.2164},
    
    # Quận Thanh Khê
    {"address": "89 Nguyễn Hữu Thọ, Thanh Khê, Đà Nẵng", "lat": 16.0731, "lng": 108.1889},
    {"address": "167 Tôn Đức Thắng, Thanh Khê, Đà Nẵng", "lat": 16.0650, "lng": 108.1917},
    {"address": "45 Hoàng Hoa Thám, Thanh Khê, Đà Nẵng", "lat": 16.0600, "lng": 108.1850},
    {"address": "234 Ông Ích Khiêm, Thanh Khê, Đà Nẵng", "lat": 16.0722, "lng": 108.1933},
    
    # Quận Sơn Trà
    {"address": "120 Võ Nguyên Giáp, Sơn Trà, Đà Nẵng", "lat": 16.0633, "lng": 108.2489},
    {"address": "456 Hoàng Sa, Sơn Trà, Đà Nẵng", "lat": 16.0525, "lng": 108.2383},
    {"address": "78 Trường Sa, Sơn Trà, Đà Nẵng", "lat": 16.0556, "lng": 108.2417},
    {"address": "345 Ngô Quyền, Sơn Trà, Đà Nẵng", "lat": 16.0678, "lng": 108.2342},
    
    # Quận Ngũ Hành Sơn
    {"address": "99 Nguyễn Tất Thành, Ngũ Hành Sơn, Đà Nẵng", "lat": 16.0308, "lng": 108.2606},
    {"address": "234 Trường Sa, Ngũ Hành Sơn, Đà Nẵng", "lat": 16.0267, "lng": 108.2522},
    {"address": "456 Dương Đình Nghệ, Ngũ Hành Sơn, Đà Nẵng", "lat": 16.0342, "lng": 108.2578},
    
    # Quận Cẩm Lệ
    {"address": "67 Tôn Thất Đạm, Cẩm Lệ, Đà Nẵng", "lat": 16.0294, "lng": 108.1933},
    {"address": "123 Lê Văn Hiến, Cẩm Lệ, Đà Nẵng", "lat": 16.0264, "lng": 108.1872},
    {"address": "89 Nguyễn Sinh Sắc, Cẩm Lệ, Đà Nẵng", "lat": 16.0317, "lng": 108.1994},
    
    # Quận Liên Chiểu
    {"address": "45 Tôn Thất Tùng, Liên Chiểu, Đà Nẵng", "lat": 16.0731, "lng": 108.1572},
    {"address": "178 Lê Đình Lý, Liên Chiểu, Đà Nẵng", "lat": 16.0686, "lng": 108.1644},
    {"address": "234 Nguyễn Tri Phương, Liên Chiểu, Đà Nẵng", "lat": 16.0764, "lng": 108.1508},
]

def update_users():
    """Cập nhật địa chỉ cho tất cả users"""
    users = User.objects.all()
    total = users.count()
    print(f"Đang cập nhật {total} users...")
    
    for idx, user in enumerate(users):
        # Lấy địa chỉ theo vòng lặp
        location = DANANG_LOCATIONS[idx % len(DANANG_LOCATIONS)]
        
        user.address = location['address']
        user.latitude = Decimal(str(location['lat']))
        user.longitude = Decimal(str(location['lng']))
        # Tạo link Google Maps
        user.address_map_url = f"https://www.google.com/maps/search/?api=1&query={location['lat']},{location['lng']}"
        user.save(update_fields=['address', 'latitude', 'longitude', 'address_map_url'])
        
        print(f"  [{idx+1}/{total}] {user.username}: {location['address']}")
    
    print(f"✅ Đã cập nhật {total} users")

def update_jobs():
    """Cập nhật địa điểm cho tất cả job posts"""
    jobs = JobPost.objects.all()
    total = jobs.count()
    print(f"\nĐang cập nhật {total} job posts...")
    
    for idx, job in enumerate(jobs):
        # Lấy địa chỉ theo vòng lặp
        location = DANANG_LOCATIONS[idx % len(DANANG_LOCATIONS)]
        
        job.location = location['address']
        job.latitude = Decimal(str(location['lat']))
        job.longitude = Decimal(str(location['lng']))
        # Tạo link Google Maps
        job.location_map_url = f"https://www.google.com/maps/search/?api=1&query={location['lat']},{location['lng']}"
        job.save(update_fields=['location', 'latitude', 'longitude', 'location_map_url'])
        
        print(f"  [{idx+1}/{total}] {job.title}: {location['address']}")
    
    print(f"✅ Đã cập nhật {total} job posts")

if __name__ == '__main__':
    print("=" * 60)
    print("CẬP NHẬT ĐỊA CHỈ VỀ KHU VỰC ĐÀ NẴNG")
    print("=" * 60)
    
    update_users()
    update_jobs()
    
    print("\n" + "=" * 60)
    print("✅ HOÀN THÀNH!")
    print("=" * 60)
