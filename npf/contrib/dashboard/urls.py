from django.conf.urls import patterns, url

from npf.contrib.dashboard.views import IndexView, BookmarkView


urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='dashboard-index'),
    url(r'^bookmark/$', BookmarkView.as_view(), name='dashboard-bookmark'),
)