import math
import random

from datetime import datetime, date, time, timedelta
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from .views_main import getSiteData
from .models import Race, RaceAssign, Team, RaceDrawMode

def combineTimeOffset(t: time, offset: timedelta):
    return (datetime.combine(date.today(), t) + offset).time()

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
    def getRaces(raceType: str, lanesPerRace: int):
        races = []
        for race in Race.objects.filter(name__startswith = raceType):
            entry = {
                'time': race.time,
                'desc': race.name,
                'lanes': []
            }

            for lnum in range(lanesPerRace):
                try:
                    attendee = RaceAssign.objects.get(race_id=race.id, lane=(lnum + 1))
                    team = Team.objects.get(id=attendee.team_id)
                except ObjectDoesNotExist:
                    attendee = None
                    team = None
                try:
                    draw = RaceDrawMode.objects.get(race_id=race.id, lane=(lnum + 1))
                except ObjectDoesNotExist:
                    draw = None
                if team:
                    entry['lanes'].append(
                        {
                            'lane': attendee.lane,
                            'team': team.name,
                            'company': team.company
                        }
                    )
                elif draw:
                    entry['lanes'].append(
                        {
                            'lane': draw.lane,
                            'team': '-',
                            'company': draw.desc
                        }
                    )
            races.append(entry)
        return races

    content = {}

    # TODO: from DB
    content['settings'] = {
        'lanesPerRace': 3,
        'heatCount': 2,
        'intervalHeat': timedelta(minutes=15),
        'intervalFinal': timedelta(minutes=15),
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
    # get heats
    for i in range(content['settings']['heatCount']):
        races = getRaces(
            '{}{}-'.format(content['settings']['heatPrefix'], i + 1),
            content['settings']['lanesPerRace']
        )
        content['timetable'].append(
            {
                'time': races[0]['time'] if len(races) > 0 else combineTimeOffset(
                    content['settings']['timeBegin'],
                    content['settings']['offsetHeat']
                ),
                'desc': 'Vorrunde {}'.format(i + 1),
                'races': races
            }
        )
    # get finals
    content['timetable'].append(
        {
            'time': combineTimeOffset(
                content['timetable'][-1]['races'][-1]['time']
                    if len(content['timetable'][-1]['races']) > 0
                    else content['timetable'][-1]['time'],
                content['settings']['offsetFinal']
            ),
            'desc': 'Finale',
            'races': getRaces(
                content['settings']['finalPrefix'],
                content['settings']['lanesPerRace']
            )
        }
    )
    content['timetable'].append(
        {
            'time': combineTimeOffset(
                content['timetable'][-1]['races'][-1]['time']
                    if len(content['timetable'][-1]['races']) > 0
                    else content['timetable'][-1]['time'],
                content['settings']['offsetCeremony']
            ),
            'desc': 'Siegerehrung am Strandschleicher'
        }
    )

    return content

def createTimeTable(settings: dict):
    # drop existing races
    RaceAssign.objects.all().delete()
    Race.objects.all().delete()
    RaceDrawMode.objects.all().delete()

    # create race tables for heats
    lanesPerRace = settings['lanesPerRace']
    start = combineTimeOffset(settings['timeBegin'], settings['offsetHeat'])
    teams = Team.objects.filter(active=True)
    teams_idx = list(range(teams.count()))
    lastHeat = []
    for hnum in range(settings['heatCount']):
        lane = 0
        rnum = 0
        random.shuffle(teams_idx)

        # assure that attendees of last race from previous heat are not in the first race from this heat
        if len(lastHeat) > 0 and len(teams_idx) > lanesPerRace:
            while True:
                redraw = False
                for i in teams_idx[:lanesPerRace]:
                    if i in lastHeat:
                        random.shuffle(teams_idx)
                        redraw = True
                        break
                if not redraw:
                    break

        # create races
        for i, t in enumerate(teams_idx):
            if teams.count() % lanesPerRace == 1 and i == teams.count() - 2:
                # in case the last race has only 1 lane occupied
                lane = 1
            else:
                lane = (lane % lanesPerRace) + 1
            # update races
            if lane == 1:
                lastHeat = []
                rnum += 1
                race = Race()
                race.time = start
                race.name = '{}{}-{}'.format(settings['heatPrefix'], hnum + 1, rnum)
                race.save()
                start = combineTimeOffset(start, settings['intervalHeat'])
            # update race assignments
            ra = RaceAssign()
            ra.race_id = Race.objects.get(name=race.name).id
            ra.team_id = teams[t].id
            ra.lane = lane
            ra.save()
            lastHeat.append(t)

    # create race tables for finals
    start = combineTimeOffset(start, settings['offsetFinal'])
    pnum = teams.count()
    rname = ''
    for rnum in range(math.ceil(teams.count() / max(1, (lanesPerRace - 1)))):
        race = Race()
        race.time = start
        race.name = '{}{}'.format(settings['finalPrefix'], rnum + 1)
        race.save()

        # create finale draw assignments
        for lnum in range(lanesPerRace) if rnum > 0 else range(max(1, (lanesPerRace - 1))):
            rdm = RaceDrawMode()
            rdm.race_id = race.id
            rdm.lane = lnum + 1
            if rnum == 0 or lnum != 0:
                rdm.desc = 'Platz {} aus VR'.format(pnum)
                pnum -= 1
            else:
                rdm.desc = 'Erster aus {}'.format(rname)
            rdm.save()

        rname = race.name
        start = combineTimeOffset(start, settings['intervalFinal'])

def timetable(request):
    siteData = {}
    siteData['settings'] = getSiteData()
    siteData['settings']['navigationCSS'] = 'menu.css'
    siteData['settings']['pageCSS'] = 'timetable.css'
    siteData['settings'].update(getTimeTableSettings())
    siteData['content'] = getTimeTableContent()

    if request.method == "POST":
        if 'create_timetable' in request.POST:
            createTimeTable(siteData['content']['settings'])

        elif 'refresh_times' in request.POST:
            # TODO
            pass
        return redirect('/timetable')

    # update data from data base
    siteData['content'] = getTimeTableContent()

    return render(request, 'timetable.html', siteData)