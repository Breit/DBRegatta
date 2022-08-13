from django.shortcuts import render

#from xml.dom import ValidationErr
#from django.forms import ValidationError
#from django.http import HttpResponseRedirect

from .views_main import *
from .views_teams import *
from .views_timetable import *

def times(request):
    siteData = getSiteData('times')
    siteData['content'] = {}
    return render(request, 'times.html', siteData)

def results(request):
    siteData = getSiteData('results')
    siteData['content'] = {}
    return render(request, 'results.html', siteData)

def settings(request):
    siteData = getSiteData('settings')
    siteData['content'] = {}
    return render(request, 'settings.html', siteData)

def djadmin(request):
    siteData = getSiteData('djadmin')
    siteData['url'] = "/admin"
    response = render(request, 'djadmin.html', siteData)
    response['Content-Security-Policy'] = "frame-ancestors 'self' http://127.0.0.1:1080"
    return response