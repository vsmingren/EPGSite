import EPGSite
from django.conf.urls.defaults import *


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^EPGSite/', include('EPGSite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    
    #(r'^images/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.IMAGES}),
    #(r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.STATIC_PATH}),
    
    (r'^$', include('epg.urls')),
    (r'^index/', include('epg.urls')),

)


