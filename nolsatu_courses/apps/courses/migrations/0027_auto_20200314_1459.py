# Generated by Django 2.2.6 on 2020-03-14 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0026_auto_20200221_0311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='status',
            field=models.PositiveIntegerField(choices=[(1, 'Daftar'), (2, 'Mulai'), (99, 'Selesai'), (100, 'Lulus')], default=1),
        ),
    ]
