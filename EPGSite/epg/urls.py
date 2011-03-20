from django.conf.urls.defaults import *
from EPGSite.epg.views import *

urlpatterns = patterns('', 
    (r'^$', showlist),
    (r'^infor/(\d*)$',inforAction),
    (r'^play/(\d*)$',playAction),
)