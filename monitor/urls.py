from django.conf.urls import patterns, url

from monitor import views

urlpatterns = patterns('',
    url(r'^api/$', views.api_in, name='api'),
    url(r'^commands/$', views.commands, name='commands'),
    url(r'^(?P<page_name>(chart|dashboard))/$', views.data_chk, name='data_chk'),
    url(r'^(?P<page_name>(chart))/(?P<cur_beer>\d+)/$', views.data_chk),
    url(r'^chart/$', views.chart, name='chart_default'),
    url(r'^chart/(?P<cur_beer>\d+)/$', views.chart),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^dashboard/update/$', views.dashboard_update, name='dashboard_update'),
    url(r'^export/$', views.export, name='export_default'),
    url(r'^$', views.data_chk),
)

#http://pythex.org/