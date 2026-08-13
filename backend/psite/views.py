"""
The error handlers, and nothing else.

`pages`, `contact`, `sitemap`, `sitemap_xml`, `get_out` and `auth_return` were
deleted along with the job-seeker templates they rendered. Their replacements:
the platform pages and the contact form are SvelteKit routes in `site/` against
`/api/v1/contact/submit/`, and the XML sitemaps are Django's own sitemap
framework wired up in `jobsp/urls.py` from `psite/sitemaps.py`.
"""

from django.shortcuts import render


def custom_404(request, exception):
    message = "Sorry, the page you requested can not be found"
    reason = "The URL may be misspelled or the page you're looking for is no longer available."

    if request.user.is_authenticated and request.user.is_staff:
        return render(
            request,
            "dashboard/404.html",
            {"message": message, "reason": reason},
            status=404,
        )
    return render(
        request, "404.html", {"message": message, "reason": reason}, status=404
    )


def custom_500(request):
    message = "500, We are sorry! The server Encountered an Internal error"
    reason = "We are unable to complete your request. Please try again later"

    if request.user.is_authenticated and request.user.is_staff:
        return render(
            request,
            "dashboard/404.html",
            {"message": message, "reason": reason},
            status=500,
        )
    return render(
        request, "404.html", {"message": message, "reason": reason}, status=500
    )
