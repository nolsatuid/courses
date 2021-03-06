# Generated by Django 2.2.6 on 2019-11-29 14:40

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0015_auto_20191125_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='collecttask',
            name='status',
            field=models.PositiveIntegerField(choices=[(1, 'Diperiksa'), (2, 'Ulangi'), (3, 'Lulus')], default=1),
        ),
        migrations.AlterField(
            model_name='taskuploadsettings',
            name='allowed_extension',
            field=taggit.managers.TaggableManager(help_text='Extensi dipisahkan dengan koma dan menggunakan titik di depan', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Ekstensi yang diizinkan '),
        ),
    ]
