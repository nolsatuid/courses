from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, AnonymousUser
from django.utils.text import slugify
from django.utils import timezone

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

    class Meta:
        verbose_name = _("course")
        verbose_name_plural = _("courses")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.slug:  # edit
            if slugify(self.title) != self.slug:
                self.slug = generate_unique_slug(Courses, self.title)
        else:  # create
            self.slug = generate_unique_slug(Courses, self.title)
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
        if now.date() >= batch.start_date and now.date() <= batch.end_date:
            return True
        else:
            return False

    def get_last_batch(self):
        batch = self.batchs.order_by('batch').last()
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
        if self.slug:  # edit
            if slugify(self.title) != self.slug:
                self.slug = generate_unique_slug(Courses, self.title)
        else:  # create
            self.slug = generate_unique_slug(Courses, self.title)
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
        if self.slug:  # edit
            if slugify(self.title) != self.slug:
                self.slug = generate_unique_slug(Courses, self.title)
        else:  # create
            self.slug = generate_unique_slug(Courses, self.title)
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

    def __str__(self):
        return self.batch


class Enrollment(models.Model):
    user = models.ForeignKey(User, related_name='enroll', on_delete=models.CASCADE)
    course = models.ForeignKey(Courses, related_name='enrolled', on_delete=models.CASCADE)
    STATUS = Choices(
        (1, 'begin', _('Mulai')),
        (2, 'finish', _('Selesai')),
    )
    status = models.PositiveIntegerField(choices=STATUS, default=STATUS.begin)
    allowed_access = models.BooleanField(_("Akses diberikan"), default=False)
    date_enrollment = models.DateField(_("Tanggal mendaftar"), auto_now_add=True)
    finishing_date = models.DateField(_("Tanggal menyelesaikan"), blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.course}"


class CollectTask(models.Model):
    user = models.ForeignKey(User, related_name='collect_task', on_delete=models.CASCADE)
    section = models.ForeignKey(Section, related_name='collect_task', on_delete=models.CASCADE)
    file = models.OneToOneField("upload_files.UploadFile", blank=True, on_delete=models.CASCADE)
    STATUS = Choices(
        (1, 'review', _('Diperiksa')),
        (2, 'repeat', _('Ulangi')),
        (3, 'pass', _('Lulus')),
    )
    status = models.PositiveIntegerField(choices=STATUS, default=STATUS.review)

    def __str__(self):
        return f"{self.user} - {self.section}"

        
class Activity(models.Model):
    user = models.ForeignKey(User, related_name='activities', on_delete=models.CASCADE)
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
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        state = self.section if self.section else self.module
        return f"{self.user} - {state.title}"
