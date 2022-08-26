from django.shortcuts import render

from .views_times import getRaceResultsTableContent
from .views_main import getSiteData

def display(request):
    siteData = getSiteData('display')
    siteData['display'] = getRaceResultsTableContent()
    return render(request, 'display.html', siteData)
