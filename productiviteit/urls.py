from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.behandelaar, name='behandelaar'),
    url(r'^behandelaar/$', views.behandelaar, name='behandelaar'),
    url(r'^behandelaar/(?P<medewerker_id>\d+)/$', views.behandelaar, name='behandelaar'),
    url(r'^vestiging/$', views.vestiging, name='vestiging'),
    url(r'^vestiging/(?P<vestiging_id>\d+)/$', views.vestiging, name='vestiging'),
    url(r'^planning/$', views.planning, name='planning'),
    url(r'^planning/(?P<planning_id>\d+)/$', views.planning, name='planning'),
    url(r'^planning/lijst/$', views.planning_lijst, name='planning_lijst'),
    url(r'^planning/lijst/(?P<medewerker_id>\d+)/$', views.planning_lijst, name='planning_lijst'),
    url(r'^ajax_data/$', views.ajax_data, name='ajax_data'),

]
