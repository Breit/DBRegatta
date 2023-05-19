from django.urls import path

from . import views, views_pdf

#URLConf
urlpatterns = [
    path('',                views.main),
    path('teams',           views.teams),
    path('times',           views.times),
    path('timetable',       views.timetable),
    path('settings',        views.settings),
    path('results',         views.results),
    path('display',         views.display),
    path('trainings',       views.trainings),
    path('calendar',        views.calendar),
    path('skippers',        views.skippers),
    path('djadmin',         views.djadmin),
    path('impressum',       views.impressum),

    path('teams/pdf',       views_pdf.teams),
    path('timetable/pdf',   views_pdf.timetable),
    path('results/pdf',     views_pdf.results)
]
