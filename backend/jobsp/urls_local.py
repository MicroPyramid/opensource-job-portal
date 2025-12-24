# Local development URLs
# This file contains URL patterns that should only be used in local development
# and not on production servers.

from django.urls import path, include
from django.conf import settings

# Local development URL patterns
local_urlpatterns = []

# Add schema viewer for local development only
local_urlpatterns += [
    path('schema-viewer/', include('schema_viewer.urls')),
]

# Add debug toolbar URLs if DEBUG is True and debug_toolbar is installed
if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    local_urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

# Add media file serving for local development
if settings.DEBUG:
    from django.conf.urls.static import static
    local_urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add django-extensions URLs if installed (for local development)
# if 'django_extensions' in settings.INSTALLED_APPS:
#     local_urlpatterns += [
#         path('django-extensions/', include('django_extensions.urls')),
#     ]

# Add silk profiler URLs if installed (for local development)
# if 'silk' in settings.INSTALLED_APPS:
#     local_urlpatterns += [
#         path('silk/', include('silk.urls', namespace='silk')),
#     ]
