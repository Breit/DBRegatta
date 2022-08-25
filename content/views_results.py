from django.shortcuts import render

from .views_times import getRaceResultsTableContent
from .views_main import getSiteData

def results(request):
    siteData = getSiteData('results')
    siteData['results'] = getRaceResultsTableContent()
    return render(request, 'results.html', siteData)
