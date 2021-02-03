import sweetify

from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from nolsatu_courses.apps.decorators import superuser_required
from .forms import FormSyncUser


@superuser_required
def sync_users(request):
    form = FormSyncUser(request.POST or None)
    if form.is_valid():
        form.sync_users()
        if len(form.reject_user) == 0:
            sweetify.sweetalert(request, "Berhasil Sync data", button=True, time=5000)
        else:
            reject_users = ", ".join(form.reject_user)
            sweetify.sweetalert(request, f"User {reject_users} tidak berhasil sync", button=True, time=10000)

    context = {
        'menu_active': 'accounts',
        'title': 'Sync User',
        'form': form,
        'title_submit': _("Proses")
    }
    return render(request, 'backoffice/form.html', context)
