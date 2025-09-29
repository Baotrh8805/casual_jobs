from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, Skill

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'normalized_name', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'normalized_name']
    list_editable = ['is_active']
    ordering = ['name']

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'user_type', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin bổ sung', {'fields': ('user_type', 'phone_number', 'date_of_birth', 'address', 'avatar')}),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_available']
    list_filter = ['is_available']
    search_fields = ['user__username', 'user__email', 'bio', 'custom_skills']
    filter_horizontal = ['skills']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('user', 'bio', 'is_available')
        }),
        ('Kỹ năng', {
            'fields': ('skills', 'custom_skills')
        }),
    )
