# Generated by Django 2.2.6 on 2020-04-28 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0031_courses_quizzes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courses',
            name='quizzes',
            field=models.ManyToManyField(to='quiz.Quiz', verbose_name='Quiz'),
        ),
    ]
