from django.conf import settings


def nolsatu_context(request):

    return {
        'nolsatu_profile_page_url': settings.NOLSATU_PROFILE_PAGE_URL,
        'nolsatu_home_page_url': settings.NOLSATU_HOST,
        'image_logo': settings.IMG_LOGO,
        'brand': settings.BRAND,
        'color_theme': settings.COLOR_THEME,
        'sidebar_color': settings.SIDEBAR_COLOR,
    }
