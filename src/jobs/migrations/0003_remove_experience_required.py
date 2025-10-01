from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_alter_jobapplication_proposed_rate_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobpost',
            name='experience_required',
        ),
    ]