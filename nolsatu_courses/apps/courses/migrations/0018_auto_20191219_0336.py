# Generated by Django 2.2.6 on 2019-12-19 03:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0017_merge_20191129_1500'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='module',
            options={'ordering': ['-order'], 'verbose_name': 'module', 'verbose_name_plural': 'modules'},
        ),
        migrations.AlterModelOptions(
            name='section',
            options={'ordering': ['-order'], 'verbose_name': 'section', 'verbose_name_plural': 'sections'},
        ),
        migrations.AddField(
            model_name='activity',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='activities_course', to='courses.Courses'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='status',
            field=models.PositiveIntegerField(choices=[(1, 'Mulai'), (2, 'Selesai')], default=1),
        ),
    ]