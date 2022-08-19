from datetime import date
from constance import config
from django.shortcuts import render, redirect

from .views_main import getSiteData

def getMainSettings():
    settings = [
        {
            'id': 'eventTitle',
            'name': config.siteNameDesc,
            'type': 'text',
            'value': config.siteName,
            'icon': 'tag'
        },
        {
            'id': 'eventDate',
            'name': config.eventDateDesc,
            'type': 'date',
            'value': config.eventDate,
            'icon': 'calendar3-event'
        },
        {
            'id': 'ownerName',
            'name': config.ownerNameDesc,
            'type': 'text',
            'value': config.ownerName,
            'icon': 'person-circle'
        },
        {
            'id': 'sponsorName',
            'name': config.sponsorNameDesc,
            'type': 'text',
            'value': config.sponsorName,
            'icon': 'building'
        },
        {
            'id': 'ownerUrl',
            'name': config.ownerUrlDesc,
            'type': 'text',
            'value': config.ownerUrl,
            'icon': 'link-45deg'
        },
        {
            'id': 'sponsorUrl',
            'name': config.sponsorUrlDesc,
            'type': 'text',
            'value': config.sponsorUrl,
            'icon': 'link-45deg'
        },
        {
            'id': 'ownerLogo',
            'name': config.ownerLogoDesc,
            'type': 'image',
            'value': config.ownerLogo,
            'icon': 'image'
        },
        {
            'id': 'sponsorLogo',
            'name': config.sponsorLogoDesc,
            'type': 'image',
            'value': config.sponsorLogo,
            'icon': 'image'
        }
    ]

    return settings

def settings(request):
    siteData = getSiteData('settings')
    siteData['controls'] = getMainSettings()

    if request.method == "POST":
        if 'eventTitle' in request.POST:
            config.siteName = request.POST['eventTitle']
        elif 'eventDate' in request.POST:
            config.eventDate = date.fromisoformat(request.POST['eventDate'])
        elif 'ownerName' in request.POST:
            config.ownerName = request.POST['ownerName']
        elif 'sponsorName' in request.POST:
            config.sponsorName = request.POST['sponsorName']
        elif 'ownerUrl' in request.POST:
            config.ownerUrl = request.POST['ownerUrl']
        elif 'sponsorUrl' in request.POST:
            config.sponsorUrl = request.POST['sponsorUrl']
        elif 'ownerLogo' in request.POST:
            config.ownerLogo = request.POST['ownerLogo']
        elif 'sponsorLogo' in request.POST:
            config.sponsorLogo = request.POST['sponsorLogo']
        return redirect('/settings')

    return render(request, 'settings.html', siteData)
