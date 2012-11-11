from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from paigow.models import Tile

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'paigow.views.home', name='home'),
    # url(r'^paigow/', include('paigow.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^paigow/tiles$',
        ListView.as_view(
            queryset=Tile.objects,
            #context_object_name='tile_list',
            #template_name='tile_list.html'
            )),
#    url(r'^(?P<pk>\d+)/$',
#        DetailView.as_view(
#            model=Poll,
#            template_name='polls/detail.html')),
)
