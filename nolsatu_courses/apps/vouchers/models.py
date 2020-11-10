from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from markdownx.models import MarkdownxField

from model_utils import Choices


class Voucher(models.Model):
    PROMO_TYPE = Choices(
        (1, 'percentage', _("Persentase")),
        (2, 'value', _("Nilai")),
    )

    code = models.CharField(_("Kode Voucher"), max_length=50)
    discount_type = models.SmallIntegerField(_("Voucher Promo Tipe"), choices=PROMO_TYPE, blank=True, null=True)
    discount_value = models.IntegerField(_("Diskon yang Diberikan"), blank=True, null=True)
    discount = models.IntegerField(_("Nominal Diskon"), default=0)
    description = MarkdownxField(_("Deskripsi Voucher Promo"), default="")
    qty = models.PositiveIntegerField(_("Jumlah"), default=0)
    product = models.ManyToManyField('products.Product')
    start_date = models.DateTimeField(_('Tanggal Voucher Berlaku'), auto_now_add=True)
    end_date = models.DateTimeField(_('Tanggal Voucher Berakhir'), auto_now_add=True)
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
    status = models.SmallIntegerField(choices=STATUS, default=STATUS)
    created_at = models.DateTimeField(_('Dibuat pada'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Diubah pada'), auto_now=True)

    class Meta:
        verbose_name = _("User Voucher")
        verbose_name_plural = _("User Vouchers")

    def __str__(self):
        return self.id
