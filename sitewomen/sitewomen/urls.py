"""
URL configuration for sitewomen project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page

from sitewomen import settings
from women.sitemaps import CategorySitemap, info_dict
from women.feeds import LatestPostFeed


sitemaps = {
    "cats": CategorySitemap,
    "blog": GenericSitemap(info_dict, priority=0.9, changefreq="daily"),
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path("social-auth/", include('social_django.urls', namespace="social")),
    path('captcha/', include('captcha.urls')),
    path('rosetta/', include('rosetta.urls')),
    path("api/", include("blog_api.urls")),
    path("sitemap.xml", cache_page(600)(sitemap), {"sitemaps": sitemaps},
             name="django.contrib.sitemaps.views.sitemap"),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

handler403 = 'women.views.tr_handler403'
handler404 = 'women.views.tr_handler404'
handler500 = 'women.views.tr_handler500'

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += i18n_patterns(
    path('', include('women.urls')),
    path(_('users/'), include('users.urls', namespace="users")),
    path(_('feeds/latest/'), LatestPostFeed(), name='latest_post_feed'),
    path(_('chat/'), include('chat.urls'))
)