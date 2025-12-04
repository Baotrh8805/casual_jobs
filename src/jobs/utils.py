"""
Utility functions cho jobs app
"""
import math
from decimal import Decimal

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Tính khoảng cách giữa 2 tọa độ GPS bằng công thức Haversine
    
    Args:
        lat1, lon1: Tọa độ điểm 1 (latitude, longitude)
        lat2, lon2: Tọa độ điểm 2 (latitude, longitude)
    
    Returns:
        float: Khoảng cách tính bằng km
    """
    # Chuyển đổi sang float nếu là Decimal
    if isinstance(lat1, Decimal):
        lat1 = float(lat1)
    if isinstance(lon1, Decimal):
        lon1 = float(lon1)
    if isinstance(lat2, Decimal):
        lat2 = float(lat2)
    if isinstance(lon2, Decimal):
        lon2 = float(lon2)
    
    # Bán kính trái đất (km)
    R = 6371.0
    
    # Chuyển đổi độ sang radian
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Tính chênh lệch
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Công thức Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    
    return round(distance, 2)


def check_distance_valid(user_lat, user_lon, job_lat, job_lon, max_distance_km=20):
    """
    Kiểm tra xem khoảng cách giữa user và job có hợp lệ không
    
    Args:
        user_lat, user_lon: Tọa độ của user
        job_lat, job_lon: Tọa độ của job
        max_distance_km: Khoảng cách tối đa cho phép (mặc định 20km)
    
    Returns:
        tuple: (is_valid: bool, distance: float, message: str)
    """
    # Kiểm tra tất cả tọa độ đều có giá trị
    if not all([user_lat, user_lon, job_lat, job_lon]):
        return False, None, "Thiếu thông tin tọa độ GPS. Vui lòng cập nhật địa chỉ trong hồ sơ."
    
    # Tính khoảng cách
    distance = calculate_distance(user_lat, user_lon, job_lat, job_lon)
    
    # Kiểm tra khoảng cách
    if distance <= max_distance_km:
        return True, distance, f"Khoảng cách: {distance} km"
    else:
        return False, distance, f"Địa điểm làm việc quá xa ({distance} km). Chỉ chấp nhận ứng viên trong bán kính {max_distance_km} km."
