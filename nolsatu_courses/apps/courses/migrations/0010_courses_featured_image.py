# Generated by Django 2.2.6 on 2019-10-30 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0009_auto_20191023_0330'),
    ]

    operations = [
        migrations.AddField(
            model_name='courses',
            name='featured_image',
            field=models.FileField(blank=True, upload_to='images/', verbose_name='Gambar Unggulan'),
        ),
    ]
