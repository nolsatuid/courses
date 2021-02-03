from django import forms
from django.utils.translation import ugettext_lazy as _
from nolsatu_courses.apps import utils


class FormSyncUser(forms.Form):
    IDENTIFICATOR = (
        ('email', 'Email'),
        ('username', 'Username')
    )
    identificator = forms.ChoiceField(
        label=_("Idenfikator"), choices=IDENTIFICATOR, required=False)
    users = forms.CharField(
        label=_("Email / Username"),
        help_text=_("Tulisakan Email/Username dan pisahkan dengan koma (,)"),
        widget=forms.Textarea
    )

    def __init__(self, *args, **kwargs):
        self.users = []
        self.reject_user = []
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        self.users = cleaned_data["users"].split(",")
        if len(self.users) == 0:
            raise forms.ValidationError("Masukan data users dengan benar sesuai petunjuk")
        if len(self.users) > 10:
            raise forms.ValidationError("Maksimum sync untuk saat ini hanya 10 users")
        return cleaned_data

    def sync_users(self):
        for user in self.users:
            identificator = user.strip("")
            utils.update_user(identificator, self.cleaned_data['identificator'])

    def get_identificator(self, identificator):
        if self.cleaned_data['identificator'] == 'email':
            return {'email': identificator}
        else:
            return {'username': identificator}
