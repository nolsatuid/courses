import typing
import uuid

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from fortuna_client.transaction import RemoteTransaction
from fortuna_client.utils import create_remote_transaction, get_remote_transaction, cancel_remote_transaction

from model_utils import Choices

from nolsatu_courses.apps import utils


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
    discount = models.IntegerField(_("Diskon"), default=0)

    def is_discount(self):
        return True if self.discount_value else False

    def __str__(self):
        return f"{self.id}-{self.course.title}"


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, verbose_name=_("Produk"), on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
    is_select = models.BooleanField(default=True)

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
        (6, 'refund', _("Refund")),
        (7, 'other', _("Other")),
        (8, 'canceled', _("Canceled"))
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

    def create_transaction(self) -> typing.Optional[RemoteTransaction]:
        if not self.remote_transaction_id:
            transaction = create_remote_transaction(self.user.id, self.grand_total)
            self.remote_transaction_id = transaction.id
            self.status = Order.STATUS.created
            self.save()

            return transaction
        else:
            return get_remote_transaction(self.remote_transaction_id)

    def get_transaction(self) -> typing.Optional[RemoteTransaction]:
        if self.remote_transaction_id:
            return get_remote_transaction(self.remote_transaction_id)

        return None

    def notify_user(self, remote_transaction: typing.Optional[RemoteTransaction] = None):
        context = {
            "order": self,
            "detail_url": settings.HOST + reverse('website:orders:details', args=(self.id,))
        }

        if not remote_transaction:
            remote_transaction = self.get_transaction()

        if remote_transaction:
            context['payment_url'] = remote_transaction.snap_redirect_url
            context['expired_at'] = remote_transaction.expired_at

        content_string = render_to_string("website/orders/notification_email.html", context)
        utils.send_notification(self.user, "Notifikasi Pembayaran Adinusa", raw_content=content_string)

    def cancel_transaction(self) -> None:
        if self.remote_transaction_id and self.status in (Order.STATUS.created, Order.STATUS.pending):
            return cancel_remote_transaction(self.remote_transaction_id)

        return None


class OrderItem(models.Model):
    product = models.ForeignKey(Product, verbose_name=_("Produk"), on_delete=models.CASCADE)
    order = models.ForeignKey(Order, verbose_name=_("Pesanan"), on_delete=models.CASCADE, related_name="orders")
    price = models.IntegerField(_("Harga"))
    name = models.CharField(_("Nama"), max_length=220)
    created_at = models.DateTimeField(_('Dibuat pada'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Diubah pada'), auto_now=True)

    def __str__(self):
        return f"{self.name}-{self.price}"
