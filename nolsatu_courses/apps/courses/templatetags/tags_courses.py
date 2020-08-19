import math

from django.template import Library
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from markdownx.utils import markdownify

from nolsatu_courses import settings
from nolsatu_courses.apps.courses.models import Enrollment

register = Library()


@register.filter(name='enrollment_status_display')
def status_to_display(status, styling=False):
    if status == Enrollment.STATUS.begin:
        status_display = _('Mulai')
        class_bagde = 'primary'
    elif status == Enrollment.STATUS.finish:
        status_display = _('Selesai')
        class_bagde = 'secondary'
    elif status == Enrollment.STATUS.register:
        status_display = _('Daftar')
        class_bagde = 'danger'
    elif status == Enrollment.STATUS.graduate:
        status_display = _('Lulus')
        class_bagde = 'success'
    else:
        return '-'

    if styling:
        return mark_safe('<span class="badge badge-%s">%s</span>' %
                         (class_bagde, status_display))
    return status_display


@register.filter(name='on_activity')
def on_activity(obj, user):
    return obj.on_activity(user)


# Register filter
@register.filter(name='sectoduration')
def sectoduration(value, arg=''):
    # Place seconds in to integer
    secs = int(value)

    # If seconds are greater than 0
    if secs > 0:
        # Place durations of given units in to variables
        daySecs = 86400
        hourSecs = 3600
        minSecs = 60

        # If short string is enabled
        if arg != "long":
            # Set short names
            dayUnitName = " day"
            hourUnitName = " hr"
            minUnitName = " min"
            secUnitName = " sec"

            # Set short duration unit splitters
            lastDurSplitter = " "
            nextDurSplitter = lastDurSplitter

        # If short string is not provided or any other value
        else:
            # Set long names
            dayUnitName = " day"
            hourUnitName = " hour"
            minUnitName = " minute"
            secUnitName = "second"

            # Set long duration unit splitters
            lastDurSplitter = " and "
            nextDurSplitter = ", "

        # Create string to hold outout
        durationString = ""

        # Calculate number of days from seconds
        days = int(math.floor(secs / int(daySecs)))

        # Subtract days from seconds
        secs = secs - (days * int(daySecs))

        # Calculate number of hours from seconds (minus number of days)
        hours = int(math.floor(secs / int(hourSecs)))

        # Subtract hours from seconds
        secs = secs - (hours * int(hourSecs))

        # Calculate number of minutes from seconds (minus number of days and hours)
        minutes = int(math.floor(secs / int(minSecs)))

        # Subtract days from seconds
        secs = secs - (minutes * int(minSecs))

        # Calculate number of seconds (minus days, hours and minutes)
        seconds = secs

        # If number of days is greater than 0
        if days > 0:
            # Add multiple days to duration string
            durationString += " " + str(days) + dayUnitName + (days > 1 and "s" or "")

        # Determine if next string is to be shown
        if hours > 0:

            # If there are no more units after this
            if minutes <= 0 and seconds <= 0:

                # Set hour splitter to last
                hourSplitter = lastDurSplitter

            # If there are unit after this
            else:
                # Set hour splitter to next
                hourSplitter = (len(durationString) > 0 and nextDurSplitter or "")

        # If number of hours is greater than 0
        if hours > 0:
            # Add multiple days to duration string
            durationString += hourSplitter + ' ' + str(hours) + hourUnitName + (hours > 1 and "s" or "")

        # Determine if next string is to be shown
        if minutes > 0:
            # If there are no more units after this
            if seconds <= 0:
                # Set minute splitter to last
                minSplitter = lastDurSplitter

            # If there are unit after this
            else:
                # Set minute splitter to next
                minSplitter = (len(durationString) > 0 and nextDurSplitter or "")

        # If number of minutes is greater than 0
        if minutes > 0:
            # Add multiple days to duration string
            durationString += minSplitter + ' ' + str(minutes) + minUnitName + (minutes > 1 and "s" or "")

        # Determine if next string is last
        if seconds > 0:
            # Set second splitter
            secSplitter = (len(durationString) > 0 and lastDurSplitter or "")

        # If number of seconds is greater than 0
        if seconds > 0:

            # Add multiple days to duration string
            durationString += secSplitter + ' ' + str(seconds) + secUnitName + (seconds > 1 and "s" or "")

        # Return duration string
        return durationString.strip()

    # If seconds are not greater than 0
    else:
        # Provide 'No duration' message
        return "No duration"


@register.filter
def show_markdown(text):
    return markdownify(text)


@register.filter
def image_markdown(text):
    return text.replace("/media", f"{settings.HOST}/media")


@register.filter
def get_toggle(identifier):
    return settings.FEATURE.get(identifier, False)


@register.filter
def keyvalue(dict, key):
    return dict.get(key, None)