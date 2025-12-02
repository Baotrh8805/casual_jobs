from django.db import migrations

def update_payment_types(apps, schema_editor):
    """Cập nhật payment_type từ 'daily' và 'fixed' thành 'shift'"""
    JobPost = apps.get_model('jobs', 'JobPost')
    
    # Cập nhật 'daily' và 'fixed' thành 'shift'
    updated = JobPost.objects.filter(payment_type__in=['daily', 'fixed']).update(payment_type='shift')
    print(f"Đã cập nhật {updated} công việc từ 'daily'/'fixed' thành 'shift'")

def reverse_payment_types(apps, schema_editor):
    """Rollback: chuyển 'shift' về 'daily'"""
    JobPost = apps.get_model('jobs', 'JobPost')
    updated = JobPost.objects.filter(payment_type='shift').update(payment_type='daily')
    print(f"Đã rollback {updated} công việc từ 'shift' về 'daily'")

class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0004_update_payment_types'),
    ]

    operations = [
        migrations.RunPython(update_payment_types, reverse_payment_types),
    ]