import json

from django.core.exceptions import PermissionDenied
from django.views.generic import View
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from npf.contrib.dashboard.models import Bookmark
from npf.core.xmin.util import json_serialize
from npf.core.xmin.util.admin import get_model_and_admin, get_admin_urls_for_model


class BookmarkView(View):

    def get(self, request):
        if not admin.site.has_permission(request):
            raise PermissionDenied

        response = {
            'success': True,
            'bookmarks': self._get_bookmarks(request, Bookmark.objects.select_related('content_type')
                                             .filter(user=request.user).order_by('-id'))
        }

        return HttpResponse(json_serialize(
            response, serialize_related=True, simplify_related=False, fields=['content_type', 'add_url', 'admin_url']
        ))

    def post(self, request):
        if not admin.site.has_permission(request):
            raise PermissionDenied

        content_types = {}

        response = {
            'success': False,
            'bookmarks': []
        }

        bookmarks_list = []
        record_id_list = []
        bookmark_name_list = []
        bookmarks = json.loads(request.body.decode('utf-8'))
        for bookmark in bookmarks:
            bookmark_name = bookmark.get('__str__', None)
            model_and_admin = get_model_and_admin(
                bookmark['content_type']['app_label'],
                bookmark['content_type']['model']
            )

            # model not registered in admin app
            if not model_and_admin:
                continue
            # user haven't permissions to app
            if not request.user.has_module_perms(bookmark['content_type']['app_label']):
                continue

            # user haven't permissions to model
            pemrs = model_and_admin[1].get_model_perms(request)
            # user have permissions to model
            if True in pemrs.values():
                ct_name = '{0}_{1}'.format(bookmark['content_type']['app_label'], bookmark['content_type']['model'])

                if not ct_name in content_types:
                    content_types.setdefault(ct_name, ContentType.objects.get(
                        app_label=bookmark['content_type']['app_label'],
                        model=bookmark['content_type']['model'])
                    )

                record_id = bookmark['record_id'] if 'record_id' in bookmark else None

                ct = content_types[ct_name]
                bookmark, create = Bookmark.objects.get_or_create(
                    content_type=ct, record_id=record_id, user=request.user
                )

                if create:
                    bookmarks_list.insert(0, bookmark)
                    record_id_list.insert(0, record_id)
                    bookmark_name_list.insert(0, bookmark_name)

                    response['success'] = True

        response['bookmarks'] = self._get_bookmarks(request, bookmarks_list, record_id_list, bookmark_name_list)

        return HttpResponse(json_serialize(
            response, serialize_related=True, simplify_related=False, fields=['content_type', 'add_url', 'admin_url', 'bookmark_name']
        ))

    def delete(self, request):
        response = {
            'success': True,
        }

        bookmarks = json.loads(request.body.decode('utf-8'))

        Bookmark.objects.filter(user=request.user, id__in=bookmarks).delete()

        return HttpResponse(json_serialize(response))

    def _get_bookmarks(self, request, bookmarks, record_id_list=None, bookmark_name_list=None):
        """
        Returns a valid user's bookmarks
        :param request:
        :return: generator
        """
        counter = -1
        for bookmark in bookmarks:
            counter += 1
            model_and_admin = get_model_and_admin(bookmark.content_type.app_label, bookmark.content_type.model)
            # model not registered in admin app
            if not model_and_admin:
                continue
            # user haven't permissions to app
            if not request.user.has_module_perms(bookmark.content_type.app_label):
                continue
            # user have permissions to model
            perms = model_and_admin[1].get_model_perms(request)
            if True in perms.values():
                urls = get_admin_urls_for_model(request, model_and_admin[0])
                bookmark.add_url = lambda: urls['add_url'] if 'add_url' in urls else ''
                if record_id_list and record_id_list[counter]:
                    bookmark.admin_url = lambda: urls['admin_url'] + record_id_list[counter] + '/'
                else:
                    bookmark.admin_url = lambda: urls['admin_url'] if 'admin_url' in urls else ''
                if bookmark_name_list and bookmark_name_list[counter]:
                    bookmark.bookmark_name = lambda: bookmark_name_list[counter]
                yield bookmark