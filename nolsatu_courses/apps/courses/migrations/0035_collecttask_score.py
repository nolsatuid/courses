# Generated by Django 2.2.6 on 2020-05-26 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0034_module_show_all_sections'),
    ]

    operations = [
        migrations.AddField(
            model_name='collecttask',
            name='score',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Nilai'),
        ),
    ]
