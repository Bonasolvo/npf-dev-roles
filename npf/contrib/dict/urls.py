from django.conf.urls import patterns, url

from npf.contrib.dict.views import *


urlpatterns = patterns('',
    url(r'^dict/send_node_move/?$', send_node_move, name='send_node_move'),
)