# Generated by Django 2.2.6 on 2019-10-23 03:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_section_files'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courses',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authors', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='courses',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='courses', to=settings.AUTH_USER_MODEL, verbose_name='users'),
        ),
        migrations.AlterField(
            model_name='section',
            name='files',
            field=models.ManyToManyField(blank=True, to='upload_files.UploadFile'),
        ),
    ]
