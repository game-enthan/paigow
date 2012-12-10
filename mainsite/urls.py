from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'paigow.views.home' ),
    url(r'login', 'paigow.views.login' ),
    url(r'register', 'paigow.views.register' ),
    url(r'^paigow/', include('paigow.urls')),
    #url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
