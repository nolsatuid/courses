# Generated by Django 2.2.6 on 2020-01-16 05:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0019_enrollment_batch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collecttask',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collect_tasks', to=settings.AUTH_USER_MODEL),
        ),
    ]