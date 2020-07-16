from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField


class Vendor(models.Model):
    name = models.CharField(_("Nama"), max_length=100)
    description = MarkdownxField(_("Deskripsi"), default="")
    users = models.OneToOneField(User, verbose_name=_("users"), related_name=_("vendors"),
                                 null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Vendor")
        verbose_name_plural = _("Vendors")

    def __str__(self):
        return self.name
