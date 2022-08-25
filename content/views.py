from django.shortcuts import render

from .views_main import getSiteData

def trainings(request):
    siteData = getSiteData('trainings')
    siteData['content'] = {}
    return render(request, 'trainings.html', siteData)

def djadmin(request):
    siteData = getSiteData('djadmin')
    siteData['url'] = "/admin"
    response = render(request, 'djadmin.html', siteData)
    response['Content-Security-Policy'] = "frame-ancestors 'self' http://127.0.0.1:1080"
    return response