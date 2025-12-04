from django import template
from datetime import date

register = template.Library()

@register.filter
def calculate_age(birth_date):
    """Tính tuổi từ ngày sinh"""
    if not birth_date:
        return None
    
    today = date.today()
    age = today.year - birth_date.year
    
    # Điều chỉnh nếu chưa đến sinh nhật trong năm nay
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    
    return age
