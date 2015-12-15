from django.conf.urls import patterns, url

from .views import *


urlpatterns = patterns('',
    url(r'data/admin/(?P<app_label>\w+)/(?P<module_name>\w+)/$', ChangeList.as_view()),
    url(r'data/admin/(?P<app_label>\w+)/(?P<module_name>\w+)/actions/$', action_list),
    url(r'data/admin/(?P<app_label>\w+)/(?P<module_name>\w+)/action/$',
        ChangeList.as_view(), {'action': 'bulk_update'}),

    url(r'data/admin/(?P<app_label>\w+)/(?P<module_name>\w+)/add/$', ItemRestApi.as_view()),
    url(r'data/admin/(?P<app_label>\w+)/(?P<module_name>\w+)/(?P<object_id>\w+)/$', ItemRestApi.as_view()),

    url(r'data/events/(?P<event_id>.+)/$', ServerEvents.as_view()),
    url(r'data/choices/$', ChoiceList.as_view()),

    url(r'data$', StartXmin.as_view(), name='xmin-data'),
    url(r'data/suggest_items/$', SuggestItems.as_view()),
)
