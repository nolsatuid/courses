# Generated by Django 2.2.6 on 2020-05-27 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0037_merge_20200526_1343'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='draft',
            field=models.BooleanField(default=False, verbose_name='Draf'),
        ),
        migrations.AddField(
            model_name='section',
            name='draft',
            field=models.BooleanField(default=False, verbose_name='Draf'),
        ),
    ]