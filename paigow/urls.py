from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView, TemplateView
from paigow.models import Tile
from paigow.views import PaiGowView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'paigow.views.home', name='home'),
    # url(r'^paigow/', include('paigow.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$',
        PaiGowView.as_view(
            template_name='paigow/base_site.html',
            )),

    url(r'^tiles[/]*$',
        ListView.as_view(
            queryset=Tile.objects.order_by('-tile_rank'),
            context_object_name='tile_list',
            #template_name='tile_list.html'
            )),

    url(r'^tiles/(?P<pk>\d+)/$',
        DetailView.as_view(
            model=Tile)),
)

