from django.conf import settings


def site_config(request):
    """Inject site customization variables into all templates."""
    return {
        "site_name": getattr(settings, "MYPRESS_SITE_NAME", "MyPress"),
        "site_subtitle": getattr(settings, "MYPRESS_SITE_SUBTITLE", ""),
        "hero_title": getattr(settings, "MYPRESS_HERO_TITLE", ""),
        "hero_subtitle": getattr(settings, "MYPRESS_HERO_SUBTITLE", ""),
        "footer_text": getattr(settings, "MYPRESS_FOOTER_TEXT", ""),
    }
