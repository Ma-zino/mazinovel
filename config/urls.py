# config/urls.py
from django.contrib import admin
from django.urls import path, include # Make sure include is imported
from django.conf import settings # Import settings
from django.conf.urls.static import static # Import static
from django.shortcuts import redirect
from novels import views as novel_views # Import views from the novels app

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include the URLs from the 'novels' app, prefixing them with 'novels/'
    path('novels/', include('novels.urls')),

    # Add this line to include Django's built-in auth URLs
    # The 'accounts/' prefix is a common convention
    path('accounts/signup/', novel_views.signup, name='signup'), # Map to the signup view
    path('accounts/', include('django.contrib.auth.urls')),

    # Add a simple root redirect (optional, but good practice)
    # Redirects the homepage '/' to '/novels/'
    path('', lambda request: redirect('novels:novel_list', permanent=False)),


]

# Add this section ONLY if DEBUG is True (for development)
# This serves media files (like novel covers) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Note: Static files (CSS, JS) are typically served automatically by runserver
    # when DEBUG=True, based on STATIC_URL. Explicitly adding static() for
    # STATIC_URL is usually only needed for production setups or specific cases.
    # The existing STATICFILES_DIRS setting is sufficient for runserver.