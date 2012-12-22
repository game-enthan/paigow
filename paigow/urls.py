from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView, TemplateView
from paigow.models import PGTile, PGGame

urlpatterns = patterns('',
  # Examples:
  # url(r'^$', 'paigow.views.home', name='home'),
  # url(r'^paigow/', include('paigow.foo.urls')),

  # Uncomment the admin/doc line below to enable admin documentation:
  # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

  # Uncomment the next line to enable the admin:
  #url(r'^admin/', include(admin.site.urls)),
  
  url(r'^$', 'paigow.views.home' ),
  url(r'^home$', 'paigow.views.home' ),
  url(r'^register$', 'paigow.views.register' ),
  url(r'^login$', 'paigow.views.login' ),
  url(r'^logout$', 'paigow.views.logout' ),
  url(r'^game/new$', 'paigow.views.new_game' ),
  url(r'^game/add$', 'paigow.views.add_game' ),
  url(r'^game/([0-9]+)$', 'paigow.views.play_game' ),
  url(r'^hand/', 'paigow.views.hand_label' ),
  
  # /tile or /tiles/ : show all the tiles
  url(r'^tiles[/]*$',
    ListView.as_view(
        queryset=PGTile.objects.order_by('-tile_rank'),
        context_object_name='tile_list',
        template_name='paigow/tile_list.html'
        )),
  
  # /tile/<id> : show tile details
  url(r'^tiles/(?P<pk>\d+)/$',
    DetailView.as_view(
        model=PGTile)),
  
)

