from datetime import datetime, date, time, timedelta
from django.shortcuts import render

from .views_main import getSiteData
from .models import Race, RaceAssign, Team

# settings for the timetable page
def getTimeTableSettings():
    settings = {
        'timetableSettingsHeader': 'Zeitplan Einstellungen',
        'timetableHeader': 'Rennplan',
        'refreshTimetableIcon': 'expired.svg',
        'refreshTimetableText': 'Zeiten aktualisieren',
        'createTimetableIcon': 'timetable.svg',
        'createTimetableText': 'Zeitplan verlosen',
        'warningCreateTimetable': 'Zeitplan komplett neu verlosen?'
    }
    return settings

def getTimeTableContent():
    def getRaces(raceType):
        races = []
        for race in Race.objects.filter(name__startswith=raceType):
            entry = {
                'time': race.time,
                'desc': race.name,
                'lanes': []
            }
            for contender in RaceAssign.objects.filter(race_id=race.id):
                team = Team.objects.get(id=contender.team_id)
                if team:
                    entry['lanes'].append(
                        {
                            'lane': contender.lane,
                            'team': team.name,
                            'company': team.company
                        }
                    )
            races.append(entry)
        return races
    
    content = {}
    
    # TODO: from DB
    content['settings'] = {
        'lanesPerRace': 3,
        'heatCount': 2,
        'intervalHeat': 15,
        'intervalFinal': 15,
        'timeBegin': time(hour=10, minute=00),
        'offsetHeat': timedelta(minutes=60),
        'offsetFinal': timedelta(minutes=45),
        'offsetCeremony': timedelta(minutes=30),
        'heatPrefix': 'V',
        'finalPrefix': 'E',
        'timetableHeader': {
            'time': 'Startzeit',
            'name': 'Lauf',
            'team': 'Team',
            'company': 'Firma',
            'lane': 'Bahn'
        }
    }
    
    content['timetable'] = []
    content['timetable'].append(
        {
            'time': content['settings']['timeBegin'],
            'desc': 'Team Captains Meeting am Strandschleicher'
        }
    )
    content['timetable'].append(
        {
            'time': (
                datetime.combine(date.today(), content['settings']['timeBegin']) +
                content['settings']['offsetHeat']
            ).time(),
            'desc': 'Vorrunde',
            'races': getRaces(content['settings']['heatPrefix'])     # get heats
        }
    )
    content['timetable'].append(
        {
            'time': (
                datetime.combine(
                    date.today(),
                    content['timetable'][-1]['races'][-1]['time']
                        if len(content['timetable'][-1]['races']) > 0
                        else content['timetable'][-1]['time']
                ) +
                content['settings']['offsetFinal']
            ).time(),
            'desc': 'Finale',
            'races': getRaces(content['settings']['finalPrefix'])    # get finals
        }
    )
    content['timetable'].append(
        {
            'time': (
                datetime.combine(
                    date.today(),
                    content['timetable'][-1]['races'][-1]['time']
                        if len(content['timetable'][-1]['races']) > 0
                        else content['timetable'][-1]['time']
                ) +
                content['settings']['offsetCeremony']
            ).time(),
            'desc': 'Siegerehrung am Strandschleicher'
        }
    )
    
    return content

def timetable(request):
    siteData = {}
    siteData['settings'] = getSiteData()
    siteData['settings']['navigationCSS'] = 'menu.css'
    siteData['settings']['pageCSS'] = 'timetable.css'
    siteData['settings'].update(getTimeTableSettings())
    siteData['content'] = getTimeTableContent()
    
    return render(request, 'timetable.html', siteData)