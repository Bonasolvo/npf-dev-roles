from django.conf import settings
from django.shortcuts import render_to_response
from django.core.exceptions import PermissionDenied
from django.views.generic import View
from django.contrib import admin
from django.core import urlresolvers

from npf.core.xmin.settings import XMIN_POLLING_INTERVAL
from npf.core.xmin.util import json_serialize
from npf.core.xmin.util.admin import get_app_list


class IndexView(View):

    def get(self, request, *args, **kwargs):
        if not admin.site.has_permission(request):
            raise PermissionDenied

        xmin_settings = {
            'site_title': admin.site.site_title,
            'urls': {
                'logout': urlresolvers.reverse('admin:logout'),
                'password_change': urlresolvers.reverse('admin:password_change'),
                'xmin_data': urlresolvers.reverse('xmin-data')
            },
            'app_list': get_app_list(request),
            'poll_interval': XMIN_POLLING_INTERVAL,
            'user': {
                'name': request.user.get_short_name() or request.user.username,
                'id': request.user.id,
            }
        }

        context = {
            'settings': json_serialize(xmin_settings),
            'DEBUG': settings.DEBUG
        }

        return render_to_response('index.html', context)