import json
import os
import zipfile

from io import StringIO, BytesIO

from django.utils.datetime_safe import datetime
from django.conf import settings

from rest_framework import serializers
from nolsatu_courses.apps.courses.models import (
    Courses, Module, Section, TaskUploadSettings
)
from nolsatu_courses.apps.utils import md_extract_img


class ExportCourse:

    timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")
    tmp_dir = settings.TMP_PRJ_DIR

    def __init__(self, course):
        self.course = course
        self.serializer = ExportCourseSerializer(self.course)
        self.data = self.serializer.data
        self.export_name = f"export-{course.slug}-{self.timestamp}"
        self.json_filename = f"{self.export_name}.json"
        self.zip_filename = f"{self.export_name}.zip"

        # The zip compressor, BytesIO to grab in-memory ZIP contents
        self.zip_buffer = BytesIO()
        self.zip_file = zipfile.ZipFile(self.zip_buffer, "w")

    def _write_to_json(self):
        """
        write json file on tmp dir
        """
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

        with open(self._tmp_file_path(), 'w') as outputfile:
            buffer = StringIO(json.dumps(self.data, indent=4))
            json.dump(buffer.getvalue(), outputfile)

    def _tmp_file_path(self):
        """
        return path from json file
        """
        return os.path.join(self.tmp_dir, self.json_filename)

    def _write_files_to_zip(self):
        """
        To get all files then include into zip
        E.g [thearchive.zip]/
            {export_name}
                export.json
                media/
                    *.jpg
                    {sub_dir}/*.png
        """
        filenames = []
        zip_subdir = self.export_name
        zip_media_dir = os.path.join(zip_subdir, "media")

        # write json file to zip
        self.zip_file.write(
            self._tmp_file_path(),
            os.path.join(zip_subdir, self.json_filename)
        )

        # write featured_image into zip
        filenames.append({
            'path': self.course.featured_image.path,
            'name': self.course.featured_image.name
        })

        for fpath in filenames:
            # Calculate path for file in zip
            fdir, fname = os.path.split(fpath['name'])
            if fdir:
                zip_sub_path = os.path.join(zip_media_dir, fdir)
                zip_path = os.path.join(zip_sub_path, fname)
            else:
                zip_path = os.path.join(zip_media_dir, fname)

            # Add file, at correct path
            self.zip_file.write(fpath['path'], zip_path)

    def _write_img_md_to_zip(self):
        """
        to write all images from markdownx models Courses, Module, Section
        """
        # get image from model Courses
        imgs = md_extract_img(self.course.description_md)
        imgs += md_extract_img(self.course.description_md)

        for module in self.course.modules.all():
            # get image from model Module
            imgs += md_extract_img(module.description_md)

            for section in module.sections.all():
                # get image from model Section
                imgs += md_extract_img(section.content_md)
                if section.is_task:
                    imgs += md_extract_img(
                        section.task_setting.instruction_md)

        # use set to remove duplicate image
        for img in set(imgs):
            path, name = os.path.split(img)

            # if first char is /, then remove it to join to work
            if path.startswith('/'):
                path = path[1:]

            subdir = os.path.join(settings.PROJECT_ROOT, path)
            full_path = os.path.join(subdir, name)
            zip_markdownx_dir = os.path.join(self.export_name, f"{path}/{name}")

            # Add file, at correct path
            self.zip_file.write(full_path, zip_markdownx_dir)

    def export_data(self):
        self._write_to_json()
        self._write_files_to_zip()
        self._write_img_md_to_zip()

        # Must close zip for all contents to be written
        self.zip_file.close()


class TaskSettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskUploadSettings
        exclude = ['section']


class ExportSectionSerializer(serializers.ModelSerializer):
    task_setting = TaskSettingSerializer(required=False)

    class Meta:
        model = Section
        exclude = ['module', 'files']


class ExportModuleSerializer(serializers.ModelSerializer):
    sections = ExportSectionSerializer(many=True)

    class Meta:
        model = Module
        exclude = ['course']


class ExportCourseSerializer(serializers.ModelSerializer):
    modules = ExportModuleSerializer(many=True)

    class Meta:
        model = Courses
        exclude = ['author', 'users', 'quizzes', 'vendor']
