from django.conf import settings
from django.core.cache import cache


def nolsatu_context(request):
    apperance = cache.get(settings.KEY_CACHE_APPERANCE, {})
    return {
        'nolsatu_profile_page_url': settings.NOLSATU_PROFILE_PAGE_URL,
        'nolsatu_home_page_url': settings.NOLSATU_HOST,
        'brand_logo': apperance.get('logo', ''),
        'brand_logo_light': apperance.get('logo_light', ''),
        'brand_logo_dark': apperance.get('logo_dark', ''),
        'brand': apperance.get('site_name', 'NolSatu'),
        'color_theme': apperance.get('color_theme', 'danger'),
        'sidebar_color': apperance.get('sidebar_color', 'light'),
    }
