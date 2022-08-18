import math
import random

from constance import config
from datetime import datetime, date, time, timedelta
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from .views_main import getSiteData
from .models import Race, RaceAssign, Team, RaceDrawMode

def combineTimeOffset(t: time, offset: timedelta):
    return (datetime.combine(date.today(), t) + offset).time()

def getTimeTableSettings():
    settings = [
        {
            'id': 'timeBegin',
            'name': config.timeBeginDesc,
            'type': 'time',
            'value': config.timeBegin,
            'icon': 'clock'
        },
        {
            'id': 'offsetHeat',
            'name': config.offsetHeatDesc,
            'type': 'number',
            'value': config.offsetHeat.seconds // 60,
            'icon': 'clock-history'
        },
        {
            'id': 'offsetFinale',
            'name': config.offsetFinaleDesc,
            'type': 'number',
            'value': config.offsetFinale.seconds // 60,
            'icon': 'clock-history'
        },
        {
            'id': 'offsetCeremony',
            'name': config.offsetCeremonyDesc,
            'type': 'number',
            'value': config.offsetCeremony.seconds // 60,
            'icon': 'clock-history'
        },
        {
            'id': 'lanesPerRace',
            'name': config.lanesPerRaceDesc,
            'type': 'number',
            'value': config.lanesPerRace,
            'min': config.lanesPerRaceMin,
            'max': config.lanesPerRaceMax,
            'icon': 'layout-three-columns'
        },
        {
            'id': 'heatCount',
            'name': config.heatCountDesc,
            'type': 'number',
            'value': config.heatCount,
            'min': config.heatCountMin,
            'max': config.heatCountMax,
            'icon': 'repeat'
        },
        {
            'id': 'intervalHeat',
            'name': config.intervalHeatDesc,
            'type': 'number',
            'value': config.intervalHeat.seconds // 60,
            'icon': 'distribute-horizontal'
        },
        {
            'id': 'intervalFinal',
            'name': config.intervalFinalDesc,
            'type': 'number',
            'value': config.intervalFinal.seconds // 60,
            'icon': 'distribute-horizontal'
        }
    ]

    return settings

def getFirstRaceTime(raceType: str):
        race = Race.objects.filter(name__startswith = raceType).order_by('time').first()
        return race.time if race else config.timeBegin

def getLastRaceTime(raceType: str):
        race = Race.objects.filter(name__startswith = raceType).order_by('time').last()
        return race.time if race else config.timeBegin

def getRaces(raceType: str):
    races = []
    for race in Race.objects.filter(name__startswith = raceType):
        entry = {
            'time': race.time,
            'desc': race.name,
            'lanes': []
        }

        # deduce lane count from database
        lanesPerRace = len(set([ra.lane for ra in RaceAssign.objects.all()]))
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
                        'team': draw.desc,
                        'company': '-'
                    }
                )

        races.append(entry)
    return races

def updateRaces(raceType: str, startTime: time, interval: timedelta):
    races = Race.objects.filter(name__startswith = raceType)
    for race in races:
        race.time = startTime
        race.save()
        startTime = combineTimeOffset(startTime, interval)
    if len(races) == 0:
        return startTime
    else:
        return combineTimeOffset(startTime, -interval)

def getTimeTableContent():
    timetable = []
    timetable.append(
        {
            # deduce starting time from first race (minus the appropriate offset)
            'time': combineTimeOffset(getFirstRaceTime('{}{}-'.format(config.heatPrefix, 1)), -config.offsetHeat),
            'desc': config.teamCaptainsMeetingTitle,
            'type': 'meeting'
        }
    )

    # get heats
    for i in range(config.heatCount):
        races = getRaces('{}{}-'.format(config.heatPrefix, i + 1))
        if len(races) > 0:
            timetable.append(
                {
                    'time': races[0]['time'] if len(races) > 0 else combineTimeOffset(
                        config.timeBegin,
                        config.offsetHeat
                    ),
                    'desc': '{} {}'.format(config.heatsTitle, i + 1),
                    'races': races,
                    'type': 'heat'
                }
            )

    # get finals
    timetable.append(
        {
            'time': combineTimeOffset(
                timetable[-1]['races'][-1]['time']
                    if 'races' in timetable[-1] and len(timetable[-1]['races']) > 0
                    else timetable[-1]['time'],
                config.offsetFinale
            ),
            'desc': config.finaleTitle,
            'races': getRaces(config.finalPrefix),
            'type': 'finale'
        }
    )

    timetable.append(
        {
            'time': combineTimeOffset(
                timetable[-1]['races'][-1]['time']
                    if 'races' in timetable[-1] and len(timetable[-1]['races']) > 0
                    else timetable[-1]['time'],
                config.offsetCeremony
            ),
            'desc': config.victoryCeremonyTitle,
            'type': 'ceremony'
        }
    )

    return timetable

def createTimeTable():
    # drop existing races
    RaceAssign.objects.all().delete()
    Race.objects.all().delete()
    RaceDrawMode.objects.all().delete()

    # create race tables for heats
    start = combineTimeOffset(config.timeBegin, config.offsetHeat)
    teams = Team.objects.filter(active=True, wait=False)
    teams_idx = list(range(teams.count()))
    lastHeat = []
    for hnum in range(config.heatCount):
        lane = 0
        rnum = 0
        random.shuffle(teams_idx)

        # assure that attendees of last race from previous heat are not in the first race from this heat
        if len(lastHeat) > 0 and len(teams_idx) > config.lanesPerRace:
            while True:
                redraw = False
                for i in teams_idx[:config.lanesPerRace]:
                    if i in lastHeat:
                        random.shuffle(teams_idx)
                        redraw = True
                        break
                if not redraw:
                    break

        # create races
        for i, t in enumerate(teams_idx):
            if teams.count() % config.lanesPerRace == 1 and i == teams.count() - 2:
                # in case the last race has only 1 lane occupied
                lane = 1
            else:
                lane = (lane % config.lanesPerRace) + 1
            # update races
            if lane == 1:
                lastHeat = []
                rnum += 1
                race = Race()
                race.time = start
                race.name = '{}{}-{}'.format(config.heatPrefix, hnum + 1, rnum)
                race.save()
                start = combineTimeOffset(start, config.intervalHeat)
            # update race assignments
            ra = RaceAssign()
            ra.race_id = Race.objects.get(name=race.name).id
            ra.team_id = teams[t].id
            ra.lane = lane
            ra.save()
            lastHeat.append(t)

    # create race tables for finals
    start = combineTimeOffset(race.time, config.offsetFinale)
    pnum = teams.count()
    rname = ''
    if teams.count() == 0:
        races = 0
    elif teams.count() == 1:
        races = 1
    else:
        races = math.ceil((teams.count() - 1) / max(1, (config.lanesPerRace - 1)))
    for rnum in range(races):
        race = Race()
        race.time = start
        race.name = '{}{}'.format(config.finalPrefix, rnum + 1)
        race.save()

        # create finale draw assignments
        if rnum == 0:
            lanes = teams.count() - (races - 1) * (config.lanesPerRace - 1)
        else:
            lanes = config.lanesPerRace
        for lnum in range(lanes):
            rdm = RaceDrawMode()
            rdm.race_id = race.id
            rdm.lane = lnum + 1
            if rnum == 0 or lnum != 0:
                rdm.desc = config.finaleTemplate1.format(pnum)
                pnum -= 1
            else:
                rdm.desc = config.finaleTemplate2.format(rname)
            rdm.save()

        rname = race.name
        start = combineTimeOffset(start, config.intervalFinal)

def updateTimeTable():
    # update all heats at once
    start = combineTimeOffset(config.timeBegin, config.offsetHeat)
    start = updateRaces(config.heatPrefix, start, config.intervalHeat)

    # update finals
    start = combineTimeOffset(start, config.offsetFinale)
    start = updateRaces(config.finalPrefix, start, config.intervalFinal)

def timetable(request):
    siteData = getSiteData('timetable')
    siteData['timetable'] = getTimeTableContent()
    siteData['controls'] = getTimeTableSettings()

    if request.method == "POST":
        if 'timeBegin' in request.POST:
            config.timeBegin = time.fromisoformat(request.POST['timeBegin'])
        elif 'offsetHeat' in request.POST:
            config.offsetHeat = timedelta(minutes=int(request.POST['offsetHeat']))
        elif 'offsetFinale' in request.POST:
            config.offsetFinale = timedelta(minutes=int(request.POST['offsetFinale']))
        elif 'offsetCeremony' in request.POST:
            config.offsetCeremony = timedelta(minutes=int(request.POST['offsetCeremony']))
        elif 'heatCount' in request.POST:
            config.heatCount = int(request.POST['heatCount'])
        elif 'lanesPerRace' in request.POST:
            config.lanesPerRace = int(request.POST['lanesPerRace'])
        elif 'intervalHeat' in request.POST:
            config.intervalHeat = timedelta(minutes=int(request.POST['intervalHeat']))
        elif 'intervalFinal' in request.POST:
            config.intervalFinal = timedelta(minutes=int(request.POST['intervalFinal']))
        elif 'create_timetable' in request.POST:
            createTimeTable()
        elif 'refresh_times' in request.POST:
            updateTimeTable()
        return redirect('/timetable')

    return render(request, 'timetable.html', siteData)