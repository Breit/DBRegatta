import math
from constance import config
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

from .views_timetable import combineTimeOffset
from .views_main import getSiteData
from .models import Race, RaceAssign, Team, RaceDrawMode

def getRaceTimes(raceType: str):
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
                        'company': team.company,
                        'time': '{:02.0f}:{:02.2f}'.format(math.floor(attendee.time / 60), attendee.time) if attendee.time else None,
                        'place': '-'
                    }
                )
            elif draw:
                entry['lanes'].append(
                    {
                        'lane': draw.lane,
                        'team': draw.desc,
                        'company': '-',
                        'time': None,
                        'place': '-'
                    }
                )
        if all(item['time'] is not None for item in entry['lanes']):
            entry['status'] = 'finished'
        elif any(item['time'] is not None for item in entry['lanes']):
            entry['status'] = 'started'
        else:
            entry['status'] = 'not_started'
        races.append(entry)
    return races

def getRaceResultsTableContent():
    timetable = []

    # get heats
    for i in range(config.heatCount):
        races = getRaceTimes('{}{}-'.format(config.heatPrefix, i + 1))
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
            'races': getRaceTimes(config.finalPrefix),
            'type': 'finale'
        }
    )

    return timetable

def getTimesControls(selected_race = None):
    controls = {
        'races': [],
        'start_time_icon': 'clock',
        'time_icon': 'clock-history',
        'selected_race': {}
    }

    for race in Race.objects.all():
        controls['races'].append(race.name)

        if selected_race is None:
            race_assigns = RaceAssign.objects.filter(race_id=race.id)
            if sum([1 if ra.time else 0 for ra in race_assigns]) < len(race_assigns):
                selected_race = {
                    'name': race.name,
                    'id': race.id,
                    'time': race.time,
                    'lanes': []
                }
                for ra in race_assigns:
                    lane = {
                        'lane': ra.lane,
                        'team': Team.objects.get(id=ra.team_id).name,
                        'place': '-',
                        'time_min': None,
                        'time_sec': None,
                        'time_msec': None
                    }
                    if ra.time:
                        time_min, time_sec = divmod(ra.time.seconds),
                        time_msec = ra.time.microseconds / 1e3
                        lane['time_min'] = '{:02.0f}'.format(time_min)
                        lane['time_sec'] = '{:02.0f}'.format(time_sec)
                        lane['time_msec'] = '{:03.0f}'.format(time_msec)
                    selected_race['lanes'].append(lane)

    controls['selected_race'] = selected_race

    return controls

def times(request):
    siteData = getSiteData('times')
    siteData['controls'] = getTimesControls()
    siteData['times'] = getRaceResultsTableContent()

    if request.method == "POST":
        # TODO
        pass

    return render(request, 'times.html', siteData)
