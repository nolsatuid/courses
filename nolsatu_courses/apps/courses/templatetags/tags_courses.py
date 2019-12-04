from django.template import Library
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from nolsatu_courses.apps.courses.models import Enrollment

register = Library()

@register.filter(name='enrollment_status_display')
def status_to_display(status, styling=False):
    if status == Enrollment.STATUS.begin:
        status_display = _('Mulai')
        class_bagde = 'success'
    elif status == Enrollment.STATUS.finish:
        status_display = _('Selesai')
        class_bagde = 'secondary'
    else:
        return '-'

    if styling:
        return mark_safe('<span class="badge badge-%s">%s</span>' %
                         (class_bagde, status_display))
    return status_display
