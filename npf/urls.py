from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.i18n import javascript_catalog

from npf.core.xmin.views import password_change_custom


urlpatterns = patterns(
    '',

    url(r'^jsi18n/', javascript_catalog),

    url(r'^admin/password_change_custom/$', password_change_custom),

    url(r'^grappelli/', include('grappelli.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^xmin/', include('npf.core.xmin.urls')),

    url(r'', include('npf.contrib.dashboard.urls')),

    url(r'^select2/', include('django_select2.urls')),

    url(r'^fias/', include('fias.urls', namespace='fias')),

    url(r'', include('npf.contrib.dict.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
