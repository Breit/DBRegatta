from django.shortcuts import render
from constance import config

# define default site data
def getSiteData():
    siteData = {
        'menu': [
            {
                'id': 'teams',
                'title': config.teamsTitle,
                'url': 'teams',
                'thumb': config.teamsIcon
            },
            {
                'id': 'timetable',
                'title': config.timetableTitle,
                'url': 'timetable',
                'thumb': config.timetableIcon
            },
            {
                'id': 'times',
                'title': config.timeTitle,
                'url': 'times',
                'thumb': config.timeIcon
            },
            {
                'id': 'results',
                'title': config.resultsTitle,
                'url': 'results',
                'thumb': config.resultsIcon
            },
            {
                'id': 'settings',
                'title': config.settingsTitle,
                'url': 'settings',
                'thumb': config.settingsIcon
            },
            {
                'id': 'admin',
                'title': config.adminTitle,
                'url': 'admin',
                'thumb': config.adminIcon
            }
        ]
    }
    return siteData

def main(request):
    return render(request, 'main.html', getSiteData())