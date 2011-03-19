from django.conf.urls.defaults import *
from EPGSite.epg.views import showlist

urlpatterns = patterns('',
    ('^$', showlist),
)