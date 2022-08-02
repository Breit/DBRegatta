from django.urls import path

from . import views

#URLConf
urlpatterns = [
    path('', views.main),
    path('teams', views.teams),
    path('times', views.times),
    path('results', views.results),
    path('timetable', views.timetable),
    path('settings', views.settings)
]