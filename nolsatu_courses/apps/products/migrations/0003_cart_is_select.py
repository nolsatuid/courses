# Generated by Django 2.2.13 on 2020-09-15 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20200914_1310'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='is_select',
            field=models.BooleanField(default=True),
        ),
    ]
