# Generated by Django 2.2.6 on 2020-05-07 22:10

import ckeditor.fields
import ckeditor_uploader.fields
from django.db import migrations
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0032_auto_20200428_1354'),
    ]

    operations = [
        migrations.AddField(
            model_name='courses',
            name='description_md',
            field=markdownx.models.MarkdownxField(default='', verbose_name='Deskripsi'),
        ),
        migrations.AddField(
            model_name='courses',
            name='short_description_md',
            field=markdownx.models.MarkdownxField(default='', verbose_name='Deskripsi Singkat'),
        ),
        migrations.AddField(
            model_name='module',
            name='description_md',
            field=markdownx.models.MarkdownxField(default='', verbose_name='Deskripsi'),
        ),
        migrations.AddField(
            model_name='section',
            name='content_md',
            field=markdownx.models.MarkdownxField(default='', verbose_name='Deskripsi'),
        ),
        migrations.AddField(
            model_name='taskuploadsettings',
            name='instruction_md',
            field=markdownx.models.MarkdownxField(default='', verbose_name='Instruksi'),
        ),
        migrations.AlterField(
            model_name='courses',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(default='', verbose_name='Deskripsi'),
        ),
        migrations.AlterField(
            model_name='courses',
            name='short_description',
            field=ckeditor.fields.RichTextField(default='', verbose_name='Deskripsi Singkat'),
        ),
        migrations.AlterField(
            model_name='module',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(default='', verbose_name='Deskripsi'),
        ),
        migrations.AlterField(
            model_name='section',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(default='', verbose_name='Deskripsi'),
        ),
        migrations.AlterField(
            model_name='taskuploadsettings',
            name='instruction',
            field=ckeditor.fields.RichTextField(default='', verbose_name='Instruksi'),
        ),
    ]
