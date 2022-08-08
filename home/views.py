from django.shortcuts import render

#from xml.dom import ValidationErr
#from django.forms import ValidationError
#from django.http import HttpResponseRedirect

from .views_main import *
from .views_teams import *
from .views_timetable import *

def times(request):
    siteData = {}
    siteData['settings'] = getSiteData()
    siteData['settings']['navigationCSS'] = 'menu.css'
    siteData['settings']['pageCSS'] = 'times.css'
    siteData['content'] = {}
    return render(request, 'times.html', siteData)

def results(request):
    siteData = {}
    siteData['settings'] = getSiteData()
    siteData['settings']['navigationCSS'] = 'menu.css'
    siteData['settings']['pageCSS'] = 'results.css'
    siteData['content'] = {}
    return render(request, 'results.html', siteData)

def settings(request):
    siteData = {}
    siteData['settings'] = getSiteData()
    siteData['settings']['navigationCSS'] = 'menu.css'
    siteData['settings']['pageCSS'] = 'settings.css'
    siteData['content'] = {}
    return render(request, 'settings.html', siteData)