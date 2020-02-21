from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, AnonymousUser
from django.utils.text import slugify
from django.utils import timezone
from django.db.models import When, Case, Count, IntegerField

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from model_utils import Choices
from taggit.managers import TaggableManager

from nolsatu_courses.apps.utils import generate_unique_slug


class Courses(models.Model):
    title = models.CharField(_("Judul"), max_length=220)
    slug = models.SlugField(max_length=200, blank=True, help_text=_("Generate otomatis jika dikosongkan"))
    short_description = RichTextField(_("Deskripsi Singkat"), config_name='basic_ckeditor')
    description = RichTextUploadingField(_("Deskripsi"))
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

    class Meta:
        verbose_name = _("course")
        verbose_name_plural = _("courses")

    def __str__(self):
        return self.title

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
        mendapatkan progres persentase pengerjaan
        """
        step_activity = self.number_of_activity_step(user)
        step_course = self.number_of_step()
        progress_on_decimal = step_activity / step_course
        progress_on_thousand = progress_on_decimal * 100

        if on_thousand:
            return progress_on_thousand
        return progress_on_decimal

    def is_complete_tasks(self, user):
        section_ids = self.modules.filter(
            sections__is_task=True).values_list('sections__id', flat=True)
        collect_tasks = CollectTask.objects.filter(
            section_id__in=section_ids, user=user
        )
        
        if len(section_ids) <= collect_tasks.count():
            return True
        return False


class Module(models.Model):
    title = models.CharField(_("Judul"), max_length=220)
    slug = models.SlugField(max_length=200, blank=True, help_text=_("Generate otomatis jika dikosongkan"))
    description = RichTextUploadingField(_("Deskripsi"))
    order = models.PositiveIntegerField(_("Urutan"))
    is_visible = models.BooleanField(_("Terlihat"), default=True)
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


class Section(models.Model):
    title = models.CharField(_("Judul"), max_length=220)
    slug = models.SlugField(max_length=200, blank=True, help_text=_("Generate otomatis jika dikosongkan"))
    content = RichTextUploadingField(_("Deskripsi"))
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


class TaskUploadSettings(models.Model):
    section = models.OneToOneField("Section", on_delete=models.CASCADE, related_name='task_setting')
    instruction = RichTextField(_("Instruksi"), config_name='basic_ckeditor')
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
    status = models.PositiveIntegerField(choices=STATUS, default=STATUS.begin)
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
            )
        )
        return count_status


class CollectTask(models.Model):
    user = models.ForeignKey(User, related_name='collect_tasks', on_delete=models.CASCADE)
    section = models.ForeignKey(Section, related_name='collect_task', on_delete=models.CASCADE)
    file = models.OneToOneField("upload_files.UploadFile", blank=True, on_delete=models.CASCADE)
    STATUS = Choices(
        (1, 'review', _('Diperiksa')),
        (2, 'repeat', _('Ulangi')),
        (3, 'graduated', _('Lulus')),
    )
    status = models.PositiveIntegerField(choices=STATUS, default=STATUS.review)
    note = models.CharField(_("Catatan"), max_length=220, blank=True, null=True)

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
