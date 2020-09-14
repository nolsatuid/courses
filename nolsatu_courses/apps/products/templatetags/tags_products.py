import math

from django.template import Library
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.products.models import Order

register = Library()


@register.filter(name='order_status_display')
def order_status_to_display(status, styling=False):
    if status == Order.STATUS.created:
        status_display = _('Dibuat')
        class_bagde = 'primary'
    elif status == Order.STATUS.success:
        status_display = _('Sukses')
        class_bagde = 'success'
    elif status == Order.STATUS.pending:
        status_display = _('Tertunda')
        class_bagde = 'warning'
    elif status == Order.STATUS.failed:
        status_display = _('Gagal')
        class_bagde = 'danger'
    elif status == Order.STATUS.expired:
        status_display = _('Kadaluarsa')
        class_bagde = 'dark'
    else:
        return '-'

    if styling:
        return mark_safe('<span class="badge badge-%s">%s</span>' %
                         (class_bagde, status_display))
    return status_display
