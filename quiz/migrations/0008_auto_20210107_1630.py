# Generated by Django 2.2.13 on 2021-01-07 09:30

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0007_question_vendor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progress',
            name='score',
            field=models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='Score'),
        ),
        migrations.AlterField(
            model_name='sitting',
            name='incorrect_questions',
            field=models.CharField(blank=True, max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='Incorrect questions'),
        ),
        migrations.AlterField(
            model_name='sitting',
            name='question_list',
            field=models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='Question List'),
        ),
        migrations.AlterField(
            model_name='sitting',
            name='question_order',
            field=models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='Question Order'),
        ),
    ]
