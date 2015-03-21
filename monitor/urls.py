from django.conf.urls import patterns, url

from monitor import views

urlpatterns = patterns('',
    url(r'^api/$', views.api, name='api'),
    url(r'^commands/$', views.commands, name='commands'),
    url(r'^commands/(?P<command_char>\S)/$', views.send_command, name='send_command'),
    url(r'^chart/$', views.chart, name='chart_default'),
    url(r'^chart/(?P<cur_beer>\d+)/$', views.chart, name='chart_beer'),
)