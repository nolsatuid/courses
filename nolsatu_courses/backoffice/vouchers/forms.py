from django import forms
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.vouchers.models import Voucher


class FormVoucher(forms.ModelForm):
    class Meta:
        model = Voucher
        exclude = ("created_at", "updated_at")
        help_texts = {
            'product': _('Tekan CTRL untuk memilih lebih dari satu'),
        }
