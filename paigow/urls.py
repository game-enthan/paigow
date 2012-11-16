from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView, TemplateView
from paigow.models import Tile

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'paigow.views.home', name='home'),
    # url(r'^paigow/', include('paigow.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$',
        TemplateView.as_view(
            template_name='paigow.html')),

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

