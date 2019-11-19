from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.utils.text import slugify

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

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.slug:  # edit
            if slugify(self.title) != self.slug:
                self.slug = generate_unique_slug(Courses, self.title)
        else:  # create
            self.slug = generate_unique_slug(Courses, self.title)
        super().save(*args, **kwargs)


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

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.slug:  # edit
            if slugify(self.title) != self.slug:
                self.slug = generate_unique_slug(Courses, self.title)
        else:  # create
            self.slug = generate_unique_slug(Courses, self.title)
        super().save(*args, **kwargs)


class TaskUploadSettings(models.Model):
    section = models.OneToOneField("Section", on_delete=models.CASCADE, related_name='task_setting')
    instruction = RichTextField(_("Instruksi"), config_name='basic_ckeditor')
    allowed_extension = TaggableManager(
        _("Ekstensi yang diizinkan "),
        help_text=_("Extensi dipisahkan dengan koma dan tanpa titik di depan")
    )
    max_size = models.IntegerField(_("Ukuran Maks"), help_text=_("Ukuran dalam MB"))

    class Meta:
        verbose_name = _("taks upload setting")
        verbose_name_plural = _("taks upload settings")

    def __str__(self):
        return self.section.title


class Batch(models.Model):
    batch = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(Courses, related_name='batchs', on_delete=models.CASCADE, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.batch


class Enrollment(models.Model):
    user = models.ForeignKey(User, related_name='enroll', on_delete=models.CASCADE)
    course = models.ForeignKey(Courses, related_name='enrolled', on_delete=models.CASCADE)
    STATUS = Choices(
        (1, 'begin', _('Begin')),
        (2, 'finish', _('Selesai')),
    )
    status = models.PositiveIntegerField(choices=STATUS, default=STATUS.begin)
    allowed_access = models.BooleanField(_("Akses diberikan"), default=True)
    date_enrollment = models.DateField(_("Tanggal mendaftar"), auto_now_add=True)
    finishing_date = models.DateField(_("Tanggal menyelesaikan"), blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.course}"
