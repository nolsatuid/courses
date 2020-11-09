import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ckeditor_uploader.fields import RichTextUploadingField


# Create your models here.


class Voucher(models.Model):
    PROMO_TYPE = [
        (1, _("Persentase")),
        (2, _("Nilai")),
    ]

    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    code = models.CharField(_("Kode Voucher"), max_length=50)
    discount_type = models.SmallIntegerField(_("Voucher Promo Tipe"), choices=PROMO_TYPE, blank=True, null=True)
    discount_value = models.IntegerField(_("Diskon yang Diberikan"), blank=True, null=True)
    discount = models.IntegerField(_("Nominal Diskon"), default=0)
    description = RichTextUploadingField(_("Deskripsi Voucher Promo"), default="")
    qty = models.PositiveIntegerField(_("Jumlah"), default=0)
    product = models.ManyToManyField('products.Product')
    start_date = models.DateTimeField(_('Tanggal Voucher Berlaku'), auto_now_add=True)
    end_date = models.DateTimeField(_('Tanggal Voucher Berakhir'), auto_now_add=True)
    created_at = models.DateTimeField(_('Dibuat pada'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Diubah pada'), auto_now=True)

    class Meta:
        verbose_name = _("Voucher")
        verbose_name_plural = _("Vouchers")

    def __str__(self):
        return self.code


class UserVoucher(models.Model):
    STATUS = [
        (1, _("Unused")),
        (2, _("Used")),
    ]

    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
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
