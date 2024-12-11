#=================================================DONE===================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # Allauth for user authentication
    path('accounts/', include('allauth.urls')),

    # Core app routes (e.g., user-related APIs)
    path('api/', include(('core.urls', 'core'), namespace='core')),

    # API app routes (e.g., product-related APIs)
    path('api/', include(('api.urls', 'api'), namespace='api')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers (optional)
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'
