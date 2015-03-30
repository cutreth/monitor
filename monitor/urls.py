from django.conf.urls import patterns, url

from monitor import views

urlpatterns = patterns('',
    url(r'^api/$', views.api, name='api'),
    url(r'^commands/$', views.commands, name='commands'),
    url(r'^commands/(?P<command_char>.+)/$', views.send_command),
    url(r'^(?P<page_name>(annotationchart|graph|dashboard))/$', views.data_chk, name='data_chk'),
    url(r'^(?P<page_name>(annotationchart|graph))/(?P<cur_beer>\d+)/$', views.data_chk),
    url(r'^graph/$', views.graph, name='graph_default'),
    url(r'^graph/(?P<cur_beer>\d+)/$', views.graph),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^dashboard/update/$', views.dashboard_update, name='dashboard_update'),
    url(r'^annotationchart/$', views.annotationchart, name='annotationchart_default'),
    url(r'^annotationchart/(?P<cur_beer>\d+)/$', views.annotationchart),
    url(r'^$', views.dashboard),
)

#http://pythex.org/