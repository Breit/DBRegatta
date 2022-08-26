from django.urls import path

from . import views
from . import views_main
from . import views_teams
from . import views_times
from . import views_timetable
from . import views_settings
from . import views_results
from . import views_display

#URLConf
urlpatterns = [
    path('',          views_main.main),
    path('teams',     views_teams.teams),
    path('times',     views_times.times),
    path('timetable', views_timetable.timetable),
    path('settings',  views_settings.settings),
    path('results',   views_results.results),
    path('display',   views_display.display),

    path('trainings', views.trainings),
    path('djadmin',   views.djadmin)
]