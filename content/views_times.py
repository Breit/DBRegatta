import math
from constance import config
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect

from .views_timetable import combineTimeOffset
from .views_main import getSiteData
from .models import Race, RaceAssign, Team, RaceDrawMode

def splitTime(race_time: float):
    minutes = math.floor(race_time / 60)
    seconds = math.floor(race_time - minutes)
    hndsecs = math.floor(100 * (race_time - math.floor(race_time)))

    return minutes, seconds, hndsecs

def getRaceTimes(raceType: str):
    races = []
    for race in Race.objects.filter(name__startswith = raceType):
        entry = {
            'time': race.time,
            'desc': race.name,
            'lanes': []
        }

        # deduce lane count from database
        lanesPerRace = len(set([attendee.lane for attendee in RaceAssign.objects.all()]))
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
                minutes, seconds, hndsecs = splitTime(attendee.time)
                entry['lanes'].append(
                    {
                        'lane': attendee.lane,
                        'team': team.name,
                        'company': team.company,
                        'time_min': minutes,
                        'time_sec': seconds,
                        'time_hnd': hndsecs,
                        'place': '?' if attendee.time != 0.0 else '-',
                        'finished': attendee.time != 0.0
                    }
                )
            elif draw:
                entry['lanes'].append(
                    {
                        'lane': draw.lane,
                        'team': draw.desc,
                        'company': '-',
                        'time_min': None,
                        'time_sec': None,
                        'time_hnd': None,
                        'place': '-',
                        'finished': False
                    }
                )
        if all(item['finished'] for item in entry['lanes']):
            entry['status'] = 'finished'
        elif any(item['finished'] for item in entry['lanes']):
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

def getTimesControls(race_id = None):
    def getSelectedRace(race_id):
        race = Race.objects.get(id=race_id)
        attendees = RaceAssign.objects.filter(race_id=race_id)
        selected_race = {
            'name': race.name,
            'id': race.id,
            'time': race.time,
            'lanes': []
        }
        for attendee in attendees:
            minutes, seconds, hndsecs = splitTime(attendee.time)
            lane = {
                'id': attendee.id,
                'lane': attendee.lane,
                'team': Team.objects.get(id=attendee.team_id).name,
                'place': '?' if attendee.time != 0.0 else '-',
                'time_min': minutes,
                'time_sec': seconds,
                'time_hnd': hndsecs,
                'finished': attendee.time != 0.0
            }
            selected_race['lanes'].append(lane)
        return selected_race

    controls = {
        'races': [],
        'start_time_icon': 'clock',
        'time_icon': 'clock-history',
        'selected_race': {}
    }

    if race_id:
        selected_race = getSelectedRace(race_id)
    else:
        selected_race = None

    for race in Race.objects.all():
        controls['races'].append(race.name)

        if selected_race is None:
            attendees = RaceAssign.objects.filter(race_id=race.id)
            if sum([1 if attendee.time else 0 for attendee in attendees]) < len(attendees):
                selected_race = getSelectedRace(race.id)

    controls['selected_race'] = selected_race

    return controls

def times(request):
    # shortcut to URL with specific race_id
    if request.method == "POST" and 'race_select' in request.POST:
        race = Race.objects.get(name = request.POST['race_select'])
        if race:
            return redirect('/times?race_id={}'.format(race.id))

    # construct site data
    siteData = getSiteData('times')
    if 'race_id' in request.GET:
        siteData['controls'] = getTimesControls(request.GET['race_id'])
    else:
        siteData['controls'] = getTimesControls()
    siteData['times'] = getRaceResultsTableContent()

    # handle POST requests
    if request.method == "POST":
        if 'refresh_times' in request.POST:
            selected_race = siteData['controls']['selected_race']
            for lane in selected_race['lanes']:
                time = float(request.POST['lane_time_min_' + lane['lane']]) * 60.0
                time += float(request.POST['lane_time_sec_' + lane['lane']])
                time += float(request.POST['lane_time_hnd_' + lane['lane']]) / 100.0
                if time == 0.0:
                    continue
                attendee = RaceAssign.objects.get(
                    id = lane['id'],
                    lane = lane['lane'],
                    race_id = selected_race['id']
                )
                # sanity check for the right team
                team = Team.objects.get(
                    id=attendee.team_id,
                    name=lane['team']
                )
                if team and attendee:
                    attendee.time = time
                    attendee.save()

            # decide which race to edit next
            if 'race_id' in request.GET:
                attendees = RaceAssign.objects.filter(race_id = request.GET['race_id'])
                if any(attendee.time == 0.0 for attendee in attendees):
                    return redirect('/times?race_id={}'.format(request.GET['race_id']))
            return redirect('/times')

        elif 'race_select' in request.POST:
            race = Race.objects.get(name = request.POST['race_select'])
            if race:
                return redirect('/times?race_id={}'.format(race.id))

    return render(request, 'times.html', siteData)
