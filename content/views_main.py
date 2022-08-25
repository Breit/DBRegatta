from django.shortcuts import render
from constance import config

from .models import Team

# define default site data
def getSiteData(id: str = None):
    siteData = {
        'menu': [
            {
                'id': 'teams',
                'title': config.teamsTitle,
                'url': 'teams',
                'thumb': config.teamsIcon,
                'active': True if id == 'teams' else False,
                'notifications': [
                    {
                        'level': 'success',
                        'count': Team.objects.filter(active=True, wait=False).count()
                    },
                    {
                        'level': 'warning',
                        'count': Team.objects.filter(active=True, wait=True).count()
                    },
                    {
                        'level': 'secondary',
                        'count': Team.objects.filter(active=False).count()
                    }
                ]
            },
            {
                'id': 'trainings',
                'title': config.trainingsTitle,
                'url': 'trainings',
                'thumb': config.trainingsIcon,
                'active': True if id == 'trainings' else False,
                'notifications': [
                    {
                        'level': 'danger',
                        'count': 'TODO'
                    }
                ]
            },
            {
                'id': 'timetable',
                'title': config.timetableTitle,
                'url': 'timetable',
                'thumb': config.timetableIcon,
                'active': True if id == 'timetable' else False
            },
            {
                'id': 'times',
                'title': config.timeTitle,
                'url': 'times',
                'thumb': config.timeIcon,
                'active': True if id == 'times' else False
            },
            {
                'id': 'results',
                'title': config.resultsTitle,
                'url': 'results',
                'thumb': config.resultsIcon,
                'active': True if id == 'results' else False,
                'notifications': [
                    {
                        'level': 'danger',
                        'count': 'TODO'
                    }
                ]
            },
            {
                'id': 'settings',
                'title': config.settingsTitle,
                'url': 'settings',
                'thumb': config.settingsIcon,
                'active': True if id == 'settings' else False
            },
            {
                'id': 'djadmin',
                'title': config.adminTitle,
                'url': 'djadmin',
                'thumb': config.adminIcon,
                'active': True if id == 'djadmin' else False
            }
        ]
    }
    return siteData

def main(request):
    return render(request, 'main.html', getSiteData())