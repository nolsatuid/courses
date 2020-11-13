from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField

from nolsatu_courses.apps.utils import image_upload_path


class Vendor(models.Model):
    name = models.CharField(_("Nama"), max_length=100)
    description = MarkdownxField(_("Deskripsi"), default="")
    users = models.ForeignKey(User, verbose_name=_("users"), related_name=_("vendors"),
                              null=True, blank=True, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to=image_upload_path('vendor'), blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)

    @property
    def get_logo_with_host(self):
        if not self.logo:
            return None

        return settings.HOST + self.logo.url

    class Meta:
        verbose_name = _("Vendor")
        verbose_name_plural = _("Vendors")

    def __str__(self):
        return self.name
