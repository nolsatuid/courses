# Generated by Django 2.2.6 on 2019-11-18 00:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0012_auto_20191111_1447'),
    ]

    operations = [
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch', models.CharField(max_length=20, unique=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveIntegerField(choices=[(1, 'Begin'), (2, 'Selesai')], default=1)),
                ('allowed_access', models.BooleanField(default=True, verbose_name='Akses diberikan')),
                ('date_enrollment', models.DateField(auto_now_add=True, verbose_name='Tanggal mendaftar')),
                ('finishing_date', models.DateField(blank=True, null=True, verbose_name='Tanggal menyelesaikan')),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='courses.Batch')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrolled', to='courses.Courses')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enroll', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
