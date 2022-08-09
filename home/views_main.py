from datetime import date
from django.shortcuts import render

# define default site data
def getSiteData():
    siteData = {
        'header': {
            'name': '14. GODYO Drachenboot-Sprint',
            'date': date(2022, 9, 10),
            'icon': 'dragon.svg',
            'url': '/'
        },
        'menu': [
            {
                'id': 'teams',
                'title': 'Teamverwaltung',
                'url': 'teams',
                'thumb': 'team.svg'
            },
            {
                'id': 'timetable',
                'title': 'Zeitplan',
                'url': 'timetable',
                'thumb': 'timetable.svg'
            },
            {
                'id': 'times',
                'title': 'Zeiteingabe',
                'url': 'times',
                'thumb': 'time.svg'
            },
            {
                'id': 'results',
                'title': 'Ergebnisse',
                'url': 'results',
                'thumb': 'results.svg'
            },
            {
                'id': 'settings',
                'title': 'Einstellungen',
                'url': 'settings',
                'thumb': 'settings.svg'
            },
            {
                'id': 'admin',
                'title': 'Admin Panel',
                'url': 'admin',
                'thumb': 'django_logo.svg'
            }
        ],
        'siteLogo': 'usv_logo.png',
        'siteCSS': 'site.css',
        'sponsor': {
            'name': 'GODYO AG',
            'logo': 'godyo_logo.png',
            'url': ''
        },
        'owner': {
            'name': 'USV Jena e.V. - Abteilung Kanu',
            'logo': 'usv_kanu_footer.png',
            'url': ''
        }
    }
    return siteData

def main(request):
    siteData = {}
    siteData['settings'] = getSiteData()
    return render(request, 'main.html', siteData)