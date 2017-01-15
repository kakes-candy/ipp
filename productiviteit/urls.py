from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^planning/$', views.planning, name='planning'),
    url(r'^planning/(?P<planning_id>\d+)/$', views.planning, name='planning'),
    url(r'^planning/lijst/$', views.planning_overzicht, name='planning_overzicht'),
    url(r'^planning/lijst/(?P<medewerker_id>\d+)/$', views.planning_overzicht, name='planning_overzicht'),
    url(r'^ajax_data/$', views.ajax_data, name='ajax_data'),

]
