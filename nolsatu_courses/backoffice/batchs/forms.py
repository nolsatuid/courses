from django import forms
from django.utils.translation import ugettext_lazy as _

from nolsatu_courses.apps.courses.models import Batch, Teach
from nolsatu_courses.apps.accounts.models import MemberNolsatu, User


class DateInput(forms.DateInput):
    input_type = 'date'


class FormBatch(forms.ModelForm):

    class Meta:
        model = Batch
        fields = ('__all__')
        labels = {
            'batch': _('Angkatan'),
            'course': _('Kursus'),
            'start_date': _('Tanggal Mulai'),
            'end_date': _('Tanggal Selesai'),
            'is_active': _('Status Aktif'),
            'link_group': _('Link Grup Telegram')
        }


class FormAssignInstructor(forms.Form):
    user = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(nolsatu__role=MemberNolsatu.ROLE.trainer), required=False
    )

    def __init__(self, batch, *args, **kwargs):
        super().__init__(*args, **kwargs)
        users = Teach.objects.filter(batch=batch).values_list('user__id', flat=True)
        self.initial['user'] = users

    def save(self, batch):
        Teach.objects.filter(batch=batch).exclude(user__in=self.cleaned_data['user']).delete()
        for user in self.cleaned_data['user']:
            Teach.objects.update_or_create(
                user=user, batch=batch,
                defaults={'user': user, 'batch': batch},
            )
