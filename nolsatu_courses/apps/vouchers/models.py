from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from markdownx.models import MarkdownxField

from model_utils import Choices

from nolsatu_courses.apps.utils import image_upload_path


class Voucher(models.Model):
    PROMO_TYPE = Choices(
        (1, 'percentage', _("Persentase")),
        (2, 'value', _("Nilai")),
    )

    code = models.CharField(_("Kode Kupon"), max_length=50)
    img = models.ImageField(_("Gambar Kupon"), upload_to=image_upload_path('vouchers'), blank=True, null=True)
    discount_type = models.SmallIntegerField(_("Tipe Kupon"), choices=PROMO_TYPE, blank=True, null=True)
    discount_value = models.IntegerField(_("Diskon yang Diberikan"), blank=True, null=True)
    description = MarkdownxField(_("Deskripsi Kupon"), default="")
    qty = models.PositiveIntegerField(_("Jumlah Kupon"), default=0)
    product = models.ManyToManyField('products.Product')
    start_date = models.DateTimeField(_('Tanggal Kupon Berlaku'))
    end_date = models.DateTimeField(_('Tanggal Kupon Berakhir'))
    created_at = models.DateTimeField(_('Dibuat pada'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Diubah pada'), auto_now=True)

    def is_expired(self):
        return True if self.end_date >= timezone.now() else False

    class Meta:
        verbose_name = _("Voucher")
        verbose_name_plural = _("Vouchers")

    def __str__(self):
        return self.code


class UserVoucher(models.Model):
    STATUS = Choices(
        (1, "Used", _("Used")),
        (2, "Unused", _("Unused")),
    )

    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
    voucher = models.ForeignKey(Voucher, verbose_name=_("Voucher"), on_delete=models.CASCADE)
    status = models.SmallIntegerField(_("Status Penggunaan Kupon"), choices=STATUS, default=STATUS.Unused)
    created_at = models.DateTimeField(_('Dibuat pada'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Diubah pada'), auto_now=True)

    class Meta:
        verbose_name = _("User Voucher")
        verbose_name_plural = _("User Vouchers")

    def __str__(self):
        return str(self.id)
