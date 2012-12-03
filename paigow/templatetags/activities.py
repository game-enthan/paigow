# This is the snippet of code that will create the 'activites' bar
# along the top of the page; it is included in most of our pages
# so is a separate html file.

from django import template

register = template.Library()

@register.inclusion_tag('paigow/activities.html')
def show_activities():
    activities = (
      { 'name': "New Game", 'url': 'game' },
      { 'name': "Continue Game", 'url': 'game/continue.html'} )
    return { 'activities' : activities }

