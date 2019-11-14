from django.conf import settings


def nolsatu_context(request):

    return {
        'nolsatu_profile_page_url': settings.NOLSATU_PROFILE_PAGE_URL,
    }
