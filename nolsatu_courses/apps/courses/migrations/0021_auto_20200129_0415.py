# Generated by Django 2.2.6 on 2020-01-29 04:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0020_auto_20200116_0502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='status',
            field=models.PositiveIntegerField(choices=[(1, 'Daftar'), (2, 'Mulai'), (99, 'Selesai')], default=2),
        ),
    ]
