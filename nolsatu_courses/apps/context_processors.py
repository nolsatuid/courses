from django.conf import settings
from django.core.cache import cache


def nolsatu_context(request):
    appearance = cache.get(settings.KEY_CACHE_APPERANCE, {})
    if settings.TOP_NAV_BG:
        bg_top_nav = settings.TOP_NAV_BG
    else:
        bg_top_nav = appearance.get('color_theme', 'danger')

    if settings.TOP_NAV_COLOR:
        color_text_top_nav = settings.TOP_NAV_COLOR
    else:
        color_text_top_nav = "dark"

    mobile_layout = request.GET.get('navbar') == "hidden" or request.is_mobile

    return {
        'nolsatu_profile_page_url': settings.NOLSATU_PROFILE_PAGE_URL,
        'nolsatu_home_page_url': settings.NOLSATU_HOST,
        'academy_home_page_url': settings.NOLSATU_HOST,
        'brand_logo': settings.NOLSATU_HOST + appearance.get('logo', ''),
        'brand_logo_light': settings.NOLSATU_HOST + appearance.get('logo_light', ''),
        'brand_logo_dark': settings.NOLSATU_HOST + appearance.get('logo_dark', ''),
        'brand_favicon': settings.NOLSATU_HOST + appearance.get('favicon', ''),
        'brand': appearance.get('site_name', 'Site Name'),
        'site_name': appearance.get('site_name', 'Site Name'),
        'color_theme': appearance.get('color_theme', 'danger'),
        'sidebar_color': appearance.get('sidebar_color', 'light'),
        'footer_title': appearance.get('footer_title', 'PT. Boer Technology (Btech)'),
        'footer_url': appearance.get('footer_url', 'https://btech.id/'),
        'hide_logo': appearance.get('hide_logo', False),
        'hide_site_name': appearance.get('hide_site_name', False),
        'color_text_top_nav': color_text_top_nav,
        'bg_top_nav': bg_top_nav,
        'mobile_layout': mobile_layout
    }
