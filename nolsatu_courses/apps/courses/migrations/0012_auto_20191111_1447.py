# Generated by Django 2.2.6 on 2019-11-11 14:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0011_courses_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='slug',
            field=models.SlugField(blank=True, help_text='Generate otomatis jika dikosongkan', max_length=200),
        ),
        migrations.AddField(
            model_name='section',
            name='slug',
            field=models.SlugField(blank=True, help_text='Generate otomatis jika dikosongkan', max_length=200),
        ),
        migrations.AlterField(
            model_name='courses',
            name='slug',
            field=models.SlugField(blank=True, help_text='Generate otomatis jika dikosongkan', max_length=200),
        ),
        migrations.AlterField(
            model_name='taskuploadsettings',
            name='section',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='task_setting', to='courses.Section'),
        ),
    ]