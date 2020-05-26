# Generated by Django 2.2.6 on 2020-05-26 04:28

from django.conf import settings
from django.db import migrations, models
import markdownx.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nama')),
                ('description', markdownx.models.MarkdownxField(default='', verbose_name='Deskripsi')),
                ('users', models.ManyToManyField(related_name='vendors', to=settings.AUTH_USER_MODEL, verbose_name='users')),
            ],
            options={
                'verbose_name': 'Vendor',
                'verbose_name_plural': 'Vendors',
            },
        ),
    ]
