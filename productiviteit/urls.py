from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^planning/$', views.planning, name='planning'),
    url(r'^planning/(?P<planning_id>\d+)/$', views.planning, name='planning'),
    url(r'^ajax_data/$', views.ajax_data, name='ajax_data'),

]
