import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from model_utils import Choices


class Product(models.Model):
    course = models.OneToOneField("courses.Courses", verbose_name=_("Kursus"),
                                  on_delete=models.CASCADE)
    price = models.IntegerField(_("Harga"))
    code = models.CharField(_("Kode"), max_length=50, blank=True, null=True)
    DISC_TYPE = Choices(
        (1, 'percentage', _("Persentase")),
        (2, 'value', _("Nilai")),
    )
    discount_type = models.SmallIntegerField(
        _("Diskon Tipe"), choices=DISC_TYPE, blank=True, null=True)
    discount_value = models.IntegerField(_("Nilai Diskon"), blank=True, null=True)
    discount = models.IntegerField(_("Diskon"), blank=True, null=True)

    def __str__(self):
        return f"{self.id}-{self.course.title}"


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, verbose_name=_("Produk"), on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.course.title}-{self.user.username}"


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
    number = models.CharField(max_length=50, unique=True)
    STATUS = Choices(
        (1, 'created', _("Created")),
        (2, 'success', _("Success")),
        (3, 'pending', _("Pending")),
        (4, 'failed', _("Failed")),
        (5, 'expired', _("Expired")),
    )
    status = models.SmallIntegerField(choices=STATUS, default=STATUS.created)
    tax = models.IntegerField(_("Pajak"), blank=True, null=True)
    discount = models.IntegerField(_("Diskon"), blank=True, null=True)
    grand_total = models.BigIntegerField(_("Grand Total"), blank=True, null=True)
    remote_transaction_id = models.CharField(max_length=220, blank=True, null=True)
    created_at = models.DateTimeField(_('Dibuat pada'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Diubah pada'), auto_now=True)

    def __str__(self):
        return f"{self.number}-{self.user.username}"


class OrderItem(models.Model):
    product = models.ForeignKey(Product, verbose_name=_("Produk"), on_delete=models.CASCADE)
    order = models.ForeignKey(Order, verbose_name=_("Pesanan"), on_delete=models.CASCADE, related_name="orders")
    price = models.IntegerField(_("Harga"))
    name = models.CharField(_("Nama"), max_length=220)
    created_at = models.DateTimeField(_('Dibuat pada'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Diubah pada'), auto_now=True)

    def __str__(self):
        return f"{self.name}-{self.price}"
