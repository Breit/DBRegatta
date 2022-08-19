from django.urls import path

from . import views
from . import views_main
from . import views_teams
from . import views_times
from . import views_timetable
from . import views_settings

#URLConf
urlpatterns = [
    path('',          views_main.main),
    path('teams',     views_teams.teams),
    path('times',     views_times.times),
    path('timetable', views_timetable.timetable),
    path('settings',  views_settings.settings),

    path('results',   views.results),
    path('trainings', views.trainings),
    path('djadmin',   views.djadmin)
]