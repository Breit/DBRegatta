from django.urls import path

from . import views

#URLConf
urlpatterns = [
    path('',          views.main),
    path('teams',     views.teams),
    path('times',     views.times),
    path('timetable', views.timetable),
    path('settings',  views.settings),
    path('results',   views.results),
    path('display',   views.display),
    path('trainings', views.trainings),
    path('djadmin',   views.djadmin),
    path('impressum', views.impressum)
]