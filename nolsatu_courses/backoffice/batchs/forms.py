from django import forms
from nolsatu_courses.apps.courses.models import Batch
from django.utils.translation import ugettext_lazy as _


class DateInput(forms.DateInput):
    input_type = 'date'


class FormBatch(forms.ModelForm):

    class Meta:
        model = Batch
        fields = ('__all__')
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
        }
        labels = {
            'batch': _('Angkatan'),
            'course': _('Kursus'),
            'start_date': _('Tanggal Mulai'),
            'end_date': _('Tanggal Selesai'),
            'is_active': _('Status Aktif'),
            'link_group': _('Link Grup Telegram')
        }
