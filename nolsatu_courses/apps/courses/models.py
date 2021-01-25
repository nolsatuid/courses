from datetime import timedelta

import pdfkit

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, AnonymousUser
from django.urls import reverse
from django.utils import timezone
from django.db.models import When, Case, Count, IntegerField
from django.template.loader import get_template
from django.http import HttpResponse

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from markdownx.models import MarkdownxField
from meta.models import ModelMeta
from model_utils import Choices
from model_utils.managers import InheritanceManager
from taggit.managers import TaggableManager

from nolsatu_courses.apps.utils import generate_unique_slug


class Courses(ModelMeta, models.Model):
    title = models.CharField(_("Judul"), max_length=220)
    slug = models.SlugField(max_length=200, blank=True, help_text=_("Generate otomatis jika dikosongkan"))
    short_description = RichTextField(_("Deskripsi Singkat"), config_name='basic_ckeditor', default="")
    description = RichTextUploadingField(_("Deskripsi"), default="")

    # Markdown Field
    short_description_md = MarkdownxField(_("Deskripsi Singkat"), default="")
    description_md = MarkdownxField(_("Deskripsi"), default="")

    featured_image = models.FileField(_("Gambar Unggulan"), upload_to="images/", blank=True)
    LEVEL = Choices(
        (1, 'beginner', _("Pemula")),
        (2, 'intermediate', _("Menengah")),
        (3, 'expert', _("Mahir"))
    )
    level = models.PositiveIntegerField(_("Level"), choices=LEVEL)
    category = TaggableManager(_("Kategori"), help_text=_("Kategori dipisahkan dengan koma"))
    users = models.ManyToManyField(User, verbose_name=_("users"), related_name="courses", blank=True)
    is_visible = models.BooleanField(_("Terlihat"), default=True)
    is_allowed = models.BooleanField(_("Diperbolehkan"), default=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="authors")
    STATUS = Choices(
        (1, 'draft', _("Konsep")),
        (2, 'publish', _("Terbit")),
    )
    status = models.PositiveIntegerField(choices=STATUS, default=STATUS.publish)
    quizzes = models.ManyToManyField('quiz.Quiz', verbose_name='Quiz')
    vendor = models.ForeignKey(
        "vendors.Vendor", verbose_name=_("Vendor"),
        on_delete=models.CASCADE, blank=True, null=True
    )

    objects = InheritanceManager()

    class Meta:
        verbose_name = _("course")
        verbose_name_plural = _("courses")

    def __str__(self):
        return self.title

    @property
    def featured_image_with_host(self):
        return settings.HOST + self.get_featured_image_url()

    @property
    def author_name(self):
        if self.vendor:
            return self.vendor.name
        return self.author.get_full_name()

    def get_featured_image_url(self):
        if self.featured_image:
            return self.featured_image.url

        from django.templatetags.static import static
        return static(settings.COURSE_IMAGE_PLACEHOLDER_STATIC)

    def save(self, *args, **kwargs):
        if self.slug:
            self.slug = generate_unique_slug(Courses, self.slug, self.id)
        else:
            self.slug = generate_unique_slug(Courses, self.title, self.id)
        super().save(*args, **kwargs)
        key = f'course-{self.id}'
        cache.delete(key)

    def category_list(self):
        return ", ".join(category.name for category in self.category.all())

    def is_started(self):
        """
        method ini digunakan untuk mengecek apakah kursus tersebut
        sudah di mulai atau belom
        """
        batch = self.get_last_batch()
        if not batch or not hasattr(batch, 'start_date'):
            return False

        now = timezone.now()
        if now.date() >= batch.start_date:
            return True
        else:
            return False

    def get_last_batch(self):
        key = f'last-batch-{self.id}'
        if cache.get(key):
            batch = cache.get(key)
        else:
            batch = self.batchs.filter(is_active=True).order_by('batch').last()
            cache.set(key, batch, 60 * 5)
        return batch

    def can_register(self, user):
        if not user.is_authenticated:
            return False

        if self.has_enrolled(user):
            return False

        return bool(self.get_last_batch()) and not self.is_started()

    def has_enrolled(self, user):
        """
        method ini digunakan untuk mengejek user tersebut
        sudah terdaftar pada kursus yang diinginkan
        """
        if user == AnonymousUser():
            return False

        course_ids = user.enroll.values_list('course__id', flat=True)
        if self.id in course_ids:
            return True
        else:
            return False

    def get_first_module(self, use_cache=False):
        if use_cache:
            key = f'course-{self.id}'
            mod_cache = cache.get(key)
            if mod_cache:
                return mod_cache

            module = self.modules.first()
            cache.set(key, module, 60 * 5)
            return module
        else:
            return self.modules.first()

    def get_enroll(self, user):
        """
        untuk mendapatkan data enroll berdasarkan user dan course
        """
        if user == AnonymousUser():
            return None
        enroll = self.enrolled.filter(user=user, batch__isnull=False).first()
        return enroll

    def number_of_step(self):
        """
        untuk mendapatkan jumlah step dari suatu course
        """
        modules_count = self.modules.all().count()
        sections_count = self.modules.aggregate(Count('sections'))['sections__count']
        count = modules_count + sections_count
        return count

    def number_of_activity_step(self, user):
        """
        untuk mendapatkan jumlah step course dari activity user
        """
        if user == AnonymousUser():
            return 0
        count = self.activities_course.filter(user=user).count()
        return count

    def progress_percentage(self, user, on_thousand=True):
        """
        mendapatkan progres persentase pengerjaan dan penyelesaian tugas
        """
        # persetase dari jumlah step
        step_activity = self.number_of_activity_step(user)
        step_course = self.number_of_step()
        progress_on_decimal = step_activity / step_course

        # persentasi dari pengerjaan tugas
        collect_tasks_on_decimal = self.progress_tasks(user)

        # progress dari semuanya
        if collect_tasks_on_decimal <= 0:
            all_progress = progress_on_decimal
        else:
            all_progress = (progress_on_decimal + collect_tasks_on_decimal) / 2

        if on_thousand:
            return all_progress * 100
        return all_progress

    def progress_tasks(self, user):
        section_ids = self.total_tasks(raw_data=True)
        collect_tasks = self.total_collect_tasks(user, section_ids)
        try:
            return collect_tasks / len(section_ids)
        except ZeroDivisionError:
            return 0

    def is_complete_tasks(self, user):
        section_ids = self.total_tasks(raw_data=True)
        collect_tasks = self.total_collect_tasks(user, section_ids)

        if len(section_ids) <= collect_tasks:
            return True
        return False

    def total_tasks(self, raw_data=False):
        section_ids = self.modules.filter(
            sections__is_task=True).values_list('sections__id', flat=True)
        if raw_data:
            return section_ids
        return len(section_ids)

    def total_collect_tasks(self, user, section_ids):
        return CollectTask.objects.filter(
            section_id__in=section_ids, user=user
        ).count()

    _metadata = {
        'title': 'title',
        'description': 'short_description',
        'image': 'get_meta_image',
        'use_og': True,
        'use_facebook': True,
        'use_twitter': True,
    }

    def get_meta_image(self):
        if self.featured_image:
            return settings.HOST + self.featured_image.url


class ModuleManager(models.Manager):
    def publish(self):
        publish = self.filter(draft=False)
        return publish


class Module(models.Model):
    title = models.CharField(_("Judul"), max_length=220)
    slug = models.SlugField(max_length=200, blank=True, help_text=_("Generate otomatis jika dikosongkan"))
    description = RichTextUploadingField(_("Deskripsi"), default="")

    # Markdown Field
    description_md = MarkdownxField(_("Deskripsi"), default="")

    order = models.PositiveIntegerField(_("Urutan"))
    is_visible = models.BooleanField(_("Terlihat"), default=False)
    course = models.ForeignKey("Courses", on_delete=models.CASCADE, related_name="modules")
    show_all_sections = models.BooleanField(
        _("Bab terlihat"), default=False,
        help_text=_("Jika di centang maka seluruh bab pada modul ini akan terlihat")
    )
    draft = models.BooleanField(_("Draf"), default=False)
    objects = ModuleManager()

    class Meta:
        verbose_name = _("module")
        verbose_name_plural = _("modules")
        ordering = ['order']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.slug:
            self.slug = generate_unique_slug(Module, self.slug, self.id)
        else:
            self.slug = generate_unique_slug(Module, self.title, self.id)

        self.sections.update(is_visible=self.show_all_sections)
        super().save(*args, **kwargs)

    def get_next(self, slugs):
        try:
            index = list(slugs).index(self.slug)
        except ValueError:
            return None

        try:
            next_slug = slugs[index + 1]
        except (AssertionError, IndexError):
            return None
        return Module.objects.filter(slug=next_slug).first()

    def get_prev(self, slugs):
        try:
            index = list(slugs).index(self.slug)
        except ValueError:
            return None

        try:
            prev_slug = slugs[index - 1]
        except (AssertionError, IndexError):
            return None
        return Module.objects.filter(slug=prev_slug).first()

    def has_enrolled(self, user):
        return self.course.has_enrolled(user)

    def on_activity(self, user):
        key = f'module-{self.id}-activity-{user.username}'
        if cache.get(key):
            activity_ids = cache.get(key)
        else:
            activity_ids = Activity.objects.filter(user=user, course=self.course) \
                .values_list('module__id', flat=True)

        try:
            if self.id in activity_ids:
                cache.set(key, activity_ids, 60 * 10)
                return True
        except TypeError:
            pass
        return False

    def delete_cache(self, user):
        cache.delete(f'module-{self.id}-activity-{user.username}')

    def sections_sorted(self):
        return self.sections.order_by('order')

    def export_to_pdf(self):
        html_template = get_template('backoffice/modules/export.html')
        section_all = self.sections.publish()
        context = {
            'module': self,
            'section_all': section_all
        }
        rendered_html = html_template.render(context)

        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        module_pdf = pdfkit.from_string(rendered_html, False, options=options)
        response = HttpResponse(module_pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=module-{self.slug}.pdf'

        return response

    def get_or_create_activity(self, user, course):
        """
        this method to handle race condition and auto delete duplicate data
        """
        activities = self.activities_module.filter(user=user, course=course)
        if activities:
            act = activities.first()
            if len(activities) > 1:
                activities.exclude(id=act.id).delete()
        else:
            act = self.activities_module.create(user=user, course=course)
        return act


class SectionManager(models.Manager):
    def publish(self):
        publish = self.filter(draft=False)
        return publish


class Section(models.Model):
    title = models.CharField(_("Judul"), max_length=220)
    slug = models.SlugField(max_length=200, blank=True, help_text=_("Generate otomatis jika dikosongkan"))
    content = RichTextUploadingField(_("Deskripsi"), default="")

    # Markdown Field
    content_md = MarkdownxField(_("Deskripsi"), default="")

    order = models.PositiveIntegerField(_("Urutan"))
    is_visible = models.BooleanField(_("Terlihat"), default=True)
    is_task = models.BooleanField(_("Tugas"), default=False)
    module = models.ForeignKey("Module", on_delete=models.CASCADE, related_name="sections")
    files = models.ManyToManyField("upload_files.UploadFile", blank=True)
    draft = models.BooleanField(_("Draf"), default=False)
    objects = SectionManager()

    class Meta:
        verbose_name = _("section")
        verbose_name_plural = _("sections")
        ordering = ['order']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.slug:
            self.slug = generate_unique_slug(Section, self.slug, self.id)
        else:
            self.slug = generate_unique_slug(Section, self.title, self.id)
        super().save(*args, **kwargs)

    def get_next(self, slugs):
        try:
            index = list(slugs).index(self.slug)
        except ValueError:
            return None

        try:
            next_slug = slugs[index + 1]
        except (AssertionError, IndexError):
            return None
        return Section.objects.filter(slug=next_slug).first()

    def get_prev(self, slugs):
        try:
            index = list(slugs).index(self.slug)
        except ValueError:
            return None

        try:
            prev_slug = slugs[index - 1]
        except (AssertionError, IndexError):
            return None
        return Section.objects.filter(slug=prev_slug).first()

    def has_enrolled(self, user):
        return self.module.course.has_enrolled(user)

    def on_activity(self, user):
        key = f'section-{self.id}-activity-{user.username}'
        if cache.get(key):
            activity_ids = cache.get(key)
        else:
            activity_ids = Activity.objects.filter(user=user, course=self.module.course) \
                .values_list('section__id', flat=True)

        try:
            if self.id in activity_ids:
                cache.set(key, activity_ids, 60 * 10)
                return True
        except TypeError:
            pass
        return False

    def delete_cache(self, user):
        cache.delete(f'section-{self.id}-activity-{user.username}')

    def get_or_create_activity(self, user, course):
        """
        this method to handle race condition and auto delete duplicate data
        """
        activities = self.activities_section.filter(user=user, course=course)
        if activities:
            act = activities.first()
            if len(activities) > 1:
                activities.exclude(id=act.id).delete()
        else:
            act = self.activities_section.create(user=user, course=course)
        return act


class TaskUploadSettings(models.Model):
    section = models.OneToOneField("Section", on_delete=models.CASCADE, related_name='task_setting')
    instruction = RichTextField(_("Instruksi"), config_name='basic_ckeditor', default="")

    # Markdown Field
    instruction_md = MarkdownxField(_("Instruksi"), default="")

    allowed_extension = TaggableManager(
        _("Ekstensi yang diizinkan "),
        help_text=_("Extensi dipisahkan dengan koma dan menggunakan titik di depan")
    )
    max_size = models.IntegerField(_("Ukuran Maks"), help_text=_("Ukuran dalam MB"))

    class Meta:
        verbose_name = _("taks upload setting")
        verbose_name_plural = _("taks upload settings")

    def __str__(self):
        return self.section.title


class Batch(models.Model):
    batch = models.CharField(max_length=20)
    course = models.ForeignKey(Courses, related_name='batchs', on_delete=models.CASCADE)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    link_group = models.URLField(blank=True, max_length=255)

    def __str__(self):
        return f"{self.batch} {self.course.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'last-batch-{self.course.id}')

    def instructor_list(self):
        return ", ".join(teach.user.first_name for teach in self.teaches.all())


class Enrollment(models.Model):
    user = models.ForeignKey(User, related_name='enroll', on_delete=models.CASCADE)
    course = models.ForeignKey(Courses, related_name='enrolled', on_delete=models.CASCADE)
    batch = models.ForeignKey(
        Batch, related_name='enrollments', on_delete=models.SET_NULL,
        blank=True, null=True
    )
    STATUS = Choices(
        (1, 'register', _('Daftar')),
        (2, 'begin', _('Mulai')),
        (99, 'finish', _('Selesai')),
        (100, 'graduate', _('Lulus'))
    )
    status = models.PositiveIntegerField(choices=STATUS, default=STATUS.register)
    allowed_access = models.BooleanField(_("Akses diberikan"), default=False)
    date_enrollment = models.DateField(_("Tanggal mendaftar"), auto_now_add=True)
    finishing_date = models.DateField(_("Tanggal menyelesaikan"), blank=True, null=True)
    final_score = models.IntegerField(_("Nilai Akhir"), default=0)
    note = models.TextField(_("Catatan"), blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.course}"

    def get_count_task_status(self):
        section_ids = CollectTask.objects.values_list('section__id', flat=True)
        count_status = self.user.collect_tasks.filter(section_id__in=section_ids).aggregate(
            graduated=Count(
                Case(When(status=CollectTask.STATUS.graduated, then=1),
                     output_field=IntegerField())
            ),
            repeat=Count(
                Case(When(status=CollectTask.STATUS.repeat, then=1),
                     output_field=IntegerField())
            ),
            review=Count(
                Case(When(status=CollectTask.STATUS.review, then=1),
                     output_field=IntegerField())
            )
        )
        return count_status

    def generate_certificate_number(self, prefix="NS-DEV") -> str:
        batch = str(self.batch.id)
        batch = "0" + batch if len(batch) == 1 else batch

        user_id = str(self.user_id)
        user_id = "0" + user_id if len(user_id) == 1 else user_id

        course_id = str(self.course_id)
        course = "0" + course_id if len(course_id) == 1 else course_id

        date = self.finishing_date.strftime("%Y-%m%d")
        certificate_number = f"{prefix}-{course}{batch}{user_id}-{date}"
        return certificate_number

    def get_cert_data(self) -> dict:
        return {
            'title': self.get_cert_title(),
            'certificate_number': self.get_cert_number(),
            'created': self.get_cert_date(),
            'user_id': self.user.nolsatu.id_nolsatu
        }

    def get_cert_title(self) -> str:
        if hasattr(self.course, 'certsetting') and \
                self.course.certsetting.cert_title:
            return self.course.certsetting.cert_title
        else:
            return self.course.title

    def get_cert_number(self) -> str:
        if hasattr(self.course, 'certsetting') and \
                self.course.certsetting.prefix_cert_number:
            prefix = self.course.certsetting.prefix_cert_number
            return self.generate_certificate_number(prefix)
        else:
            return self.generate_certificate_number()

    def get_cert_date(self) -> str:
        if hasattr(self.course, 'certsetting') and \
                self.course.certsetting.static_date:
            return self.course.certsetting.static_date.strftime("%d-%m-%Y")
        else:
            return self.finishing_date.strftime("%d-%m-%Y")

    @property
    def date_limit_access(self):
        return self.batch.start_date + timedelta(days=365)


class CollectTask(models.Model):
    user = models.ForeignKey(User, related_name='collect_tasks', on_delete=models.CASCADE)
    section = models.ForeignKey(Section, related_name='collect_task', on_delete=models.CASCADE)
    file = models.OneToOneField("upload_files.UploadFile", blank=True, null=True, on_delete=models.CASCADE)
    STATUS = Choices(
        (1, 'review', _('Diperiksa')),
        (2, 'repeat', _('Ulangi')),
        (3, 'graduated', _('Lulus')),
        (4, 'not_pass', _('Tidak Lulus')),
    )
    status = models.PositiveIntegerField(choices=STATUS, default=STATUS.review)
    note = models.TextField(_("Catatan"), blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    score = models.PositiveIntegerField(_("Nilai"), null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.section}"


class Activity(models.Model):
    user = models.ForeignKey(User, related_name='activities', on_delete=models.CASCADE)
    course = models.ForeignKey(
        Courses, related_name='activities_course',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    module = models.ForeignKey(
        Module, related_name='activities_module',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    section = models.ForeignKey(
        Section, related_name='activities_section',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        state = self.section if self.section else self.module
        return f"{self.user} - {state.title}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'course', 'module', 'section'], name='unique_activity')
        ]


class CertSetting(models.Model):
    course = models.OneToOneField(Courses, on_delete=models.CASCADE)
    cert_title = models.CharField(max_length=220, blank=True, null=True)
    prefix_cert_number = models.CharField(max_length=50, blank=True, null=True)
    static_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = _("Certificate Setting")
        verbose_name_plural = _("Certificate Settings")

    def __str__(self):
        return self.course.title


class Teach(models.Model):
    user = models.ForeignKey(User, related_name='teaches', on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, related_name='teaches', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)
