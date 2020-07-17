from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def index(request):
    template_name = 'backoffice/index.html'
    context = {}
    return render(request, template_name, context)
