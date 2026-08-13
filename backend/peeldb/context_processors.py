from django.conf import settings


def get_pj_icons(request):
    logos = {
        "jobopenings": "http://cdn.peeljobs.com/jobopenings1.png",
        "logo": "https://cdn.peeljobs.com/logo.png",
        "favicon": "https://cdn.peeljobs.com/favicon.png",
        "cdn_path": "https://cdn.peeljobs.com/",
    }
    return logos


def frontend_urls(request):
    """
    Where the public site lives, for admin templates that link out to it.

    The dashboard used to `{% url %}` job-seeker routes directly, back when
    Django rendered them. It does not any more, and those are separate origins
    now, so the links have to be absolute.
    """
    return {
        "site_url": settings.SITE_FRONTEND_URL.rstrip("/"),
        "recruiter_url": settings.RECRUITER_FRONTEND_URL.rstrip("/"),
    }
