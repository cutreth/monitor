from django.conf.urls import patterns, url

from monitor import views

urlpatterns = patterns('',
    url(r'^api/$', views.api, name='api'),
    url(r'^commands/$', views.commands, name='commands'),
    url(r'^commands/(?P<command_char>.+)/$', views.send_command),
    url(r'^graph/$', views.graph, name='graph_default'),
    url(r'^graph/(?P<cur_beer>\d+)/$', views.graph),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^dashboard/update/$', views.dashboard_update, name='dashboard_update'),
    url(r'^annotationchart/$', views.annotationchart, name='annotationchart'),
    url(r'^$', views.dashboard),
)

#http://pythex.org/