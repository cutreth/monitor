from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    #url(r'^admin/commands/$', 'monitor.views.commands', name='commands'),
    #url(r'^admin/commands/(?P<command_char>.+)/$', 'monitor.views.send_command'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^monitor/', include('monitor.urls')),
)
