from django.conf import settings
from django.core.cache import cache


def nolsatu_context(request):
    apperance = cache.get(settings.KEY_CACHE_APPERANCE, {})
    return {
        'nolsatu_profile_page_url': settings.NOLSATU_PROFILE_PAGE_URL,
        'nolsatu_home_page_url': settings.NOLSATU_HOST,
        'brand_logo': settings.NOLSATU_HOST + apperance.get('logo', ''),
        'brand_logo_light': settings.NOLSATU_HOST + apperance.get('logo_light', ''),
        'brand_logo_dark': settings.NOLSATU_HOST + apperance.get('logo_dark', ''),
        'brand_favicon': settings.NOLSATU_HOST + apperance.get('brand_favicon', ''),
        'brand': apperance.get('site_name', 'NolSatu'),
        'color_theme': apperance.get('color_theme', 'danger'),
        'sidebar_color': apperance.get('sidebar_color', 'light'),
        'footer_title': apperance.get('footer_title', 'PT. Boer Technology (Btech)'),
        'footer_url': apperance.get('footer_url', 'https://btech.id/'),
        'hide_logo': apperance.get('hide_logo', False),
        'hide_site_name': apperance.get('hide_site_name', False),
    }
