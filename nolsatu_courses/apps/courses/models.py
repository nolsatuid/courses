from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, AnonymousUser
from django.urls import reverse
from django.utils import timezone
from django.db.models import When, Case, Count, IntegerField

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from markdownx.models import MarkdownxField
from model_utils import Choices
from model_utils.managers import InheritanceManager
from taggit.managers import TaggableManager

from nolsatu_courses.apps.utils import generate_unique_slug


class Courses(models.Model):
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

    objects = InheritanceManager()

    class Meta:
        verbose_name = _("course")
        verbose_name_plural = _("courses")

    def __str__(self):
        return self.title

    @property
    def featured_image_with_host(self):
        if self.featured_image:
            return settings.HOST + self.featured_image.url
        else:
            return None

    @property
    def author_name(self):
        return self.author.get_full_name()

    def save(self, *args, **kwargs):
        if self.slug:
            self.slug = generate_unique_slug(Courses, self.slug, self.id)
        else:
            self.slug = generate_unique_slug(Courses, self.title, self.id)
        super().save(*args, **kwargs)

    def category_list(self):
        return ", ".join(category.name for category in self.category.all())

    def is_started(self):
        """
        method ini digunakan untuk mengecek apakah kursus tersebut
        sudah di mulai atau belom
        """
        batch = self.get_last_batch()
        if not batch:
            return False

        now = timezone.now()
        if now.date() >= batch.start_date:
            return True
        else:
            return False

    def get_last_batch(self):
        batch = self.batchs.filter(is_active=True).order_by('batch').last()
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

    def get_first_module(self):
        module = self.modules.first()
        return module

    def get_enroll(self, user):
        """
        untuk mendapatkan data enroll berdasarkan user dan course
        """
        if user == AnonymousUser():
            return None
        enroll = self.enrolled.filter(user=user).first()
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


class Module(models.Model):
    title = models.CharField(_("Judul"), max_length=220)
    slug = models.SlugField(max_length=200, blank=True, help_text=_("Generate otomatis jika dikosongkan"))
    description = RichTextUploadingField(_("Deskripsi"), default="")

    # Markdown Field
    description_md = MarkdownxField(_("Deskripsi"), default="")

    order = models.PositiveIntegerField(_("Urutan"))
    is_visible = models.BooleanField(_("Terlihat"), default=False)
    course = models.ForeignKey("Courses", on_delete=models.CASCADE, related_name="modules")

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
        super().save(*args, **kwargs)

    def get_next(self, slugs):
        index = list(slugs).index(self.slug)
        try:
            next_slug = slugs[index + 1]
        except (AssertionError, IndexError):
            next_slug = None
        return Module.objects.filter(slug=next_slug).first()

    def get_prev(self, slugs):
        index = list(slugs).index(self.slug)
        try:
            prev_slug = slugs[index - 1]
        except (AssertionError, IndexError):
            prev_slug = None
        return Module.objects.filter(slug=prev_slug).first()

    def has_enrolled(self, user):
        return self.course.has_enrolled(user)

    def on_activity(self, user):
        activity_ids = Activity.objects.filter(user=user, course=self.course) \
            .values_list('module__id', flat=True)

        if self.id in activity_ids:
            return True
        return False

    def api_detail_url(self):
        return settings.HOST + reverse("api:courses:module_detail", args=[self.id])

    def api_preview_url(self):
        return settings.HOST + reverse("api:courses:module_preview", args=[self.id])


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
        index = list(slugs).index(self.slug)
        try:
            next_slug = slugs[index + 1]
        except (AssertionError, IndexError):
            next_slug = None
        return Section.objects.filter(slug=next_slug).first()

    def get_prev(self, slugs):
        index = list(slugs).index(self.slug)
        try:
            prev_slug = slugs[index - 1]
        except (AssertionError, IndexError):
            prev_slug = None
        return Section.objects.filter(slug=prev_slug).first()

    def has_enrolled(self, user):
        return self.module.course.has_enrolled(user)

    def on_activity(self, user):
        activity_ids = Activity.objects.filter(user=user, course=self.module.course) \
            .values_list('section__id', flat=True)

        if self.id in activity_ids:
            return True
        return False

    def api_detail_url(self):
        return settings.HOST + reverse("api:courses:section_detail", args=[self.id])

    def api_preview_url(self):
        return settings.HOST + reverse("api:courses:section_preview", args=[self.id])


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

    def generate_certificate_number(self):
        batch = str(self.batch.batch)
        batch = "0" + batch if len(batch) == 1 else batch

        user_id = str(self.user_id)
        user_id = "0" + user_id if len(user_id) == 1 else user_id

        date = self.finishing_date.strftime("%Y-%m%d")
        certificate_number = f"NS-DEV-{batch}{user_id}-{date}"
        return certificate_number


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
    note = models.CharField(_("Catatan"), max_length=220, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_at = models.DateTimeField(auto_now=True, null=True, blank=True)

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
