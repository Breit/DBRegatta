import math
import random
from datetime import datetime, date, time, timedelta

from constance import config
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.forms.models import model_to_dict

from .models import Race, RaceAssign, Team, RaceDrawMode
from .forms import TeamForm

def loginUser(request, site: str = ''):
    if request.method == "POST":
        if 'login' in request.POST:
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                login(request, user)
                return redirect('/{}'.format(site))

        if 'logout' in request.POST:
            logout(request)
            return redirect('/{}'.format(site))

# get teams list from database
def getTeamContent():
    content = { 'teams': [] }
    for team in Team.objects.all():
        content['teams'].append(model_to_dict(team))
    content['activeTeams'] = Team.objects.filter(active=True, wait=False).count()
    content['inactiveTeams'] = Team.objects.filter(active=False).count()
    content['waitlistTeams'] = Team.objects.filter(active=True, wait=True).count()
    content['totalTeams'] = Team.objects.all().count()
    content['forms'] = {
        'form': TeamForm(),
        'add': False,
        'mod': False,
        'id': None
    }
    return content

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

def getCurrentTimeTable():
    timetable = None

    # get current heats
    for i in range(config.heatCount):
        races = getRaceTimes('{}{}-'.format(config.heatPrefix, i + 1))
        if len(races) > 0 and all(['lanes' in race for race in races]):
            if all([all(lane['time'] > 0.0 for lane in race['lanes']) for race in races]):
                # current heat already complete
                continue

            timetable = {
                    'time': races[0]['time'] if len(races) > 0 else combineTimeOffset(
                        config.timeBegin,
                        config.offsetHeat
                    ),
                    'desc': '{} {}'.format(config.heatsTitle, i + 1),
                    'races': races,
                    'type': 'heat'
                }
            break

    # get final if heats are finished
    if timetable is None:
        races = getRaceTimes(config.finalPrefix)
        timetable = {
                'time': races[0]['time'] if len(races) > 0 else combineTimeOffset(
                    config.timeBegin,
                    config.offsetFinale
                ),
                'desc': config.finaleTitle,
                'races': races,
                'type': 'finale'
            }

    return timetable

def getRankings():
    # get race times
    times = {}
    for race in Race.objects.filter(name__startswith = config.heatPrefix):
        for attendee in RaceAssign.objects.filter(race_id=race.id):
            if attendee.team_id not in times:
                times[attendee.team_id] = []
            times[attendee.team_id].append(attendee.time)

    # sort teams into brackets according to how many races they have finished
    brackets = {}
    for i in range(config.heatCount + 1):
        brackets[i] = []
    for t in times.items():
        brackets[len([x for x in t[1] if x > 0.0])].append(t)

    # sort brackets
    for k in brackets.keys():
        if k > 0:
            brackets[k] = sorted(brackets[k], key=lambda t: sum(t[1]))

    # convert brackets back to ranking table
    rankings = []
    rank = 1
    for r in reversed(range(config.heatCount + 1)):
        for t in brackets[r]:
            rankings.append(
                {
                    'rank': rank if r > 0 else 0,
                    'team_id': t[0],
                    'times': t[1],
                    'races': r
                }
            )
            rank += 1

    return rankings

def getRankingTable():
    rankingTable = {
        'desc': config.displayRankings,
        'heats': ['{}{}'.format(config.heatPrefix, i + 1) for i in range(config.heatCount)],
        'ranks': [],
        'brackets': []
    }

    for r in getRankings():
        team = Team.objects.get(id=r['team_id'])
        if team:
            rankingTable['ranks'].append(
                {
                    'id': team.id,
                    'name': team.name,
                    'company': team.company,
                    'times': r['times'],
                    'rank': r['rank'],
                    'races': r['races']
                }
            )
            if r['races'] not in rankingTable['brackets']:
                rankingTable['brackets'].append(r['races'])

    rankingTable['brackets'] = sorted(rankingTable['brackets'], reverse=True)

    return rankingTable

# get current race block (Heat# or Final) for notifications
def getCurrentRaceBlock():
    current_race_block = None
    heats_started = False
    for i in range(config.heatCount):
        races = getRaceTimes('{}{}-'.format(config.heatPrefix, i + 1))
        if len(races) > 0 and all(['lanes' in race for race in races]):
            if any([any(lane['time'] > 0.0 for lane in race['lanes']) for race in races]):
                heats_started = True
                if all([all(lane['time'] > 0.0 for lane in race['lanes']) for race in races]):
                    # current heat already complete
                    continue
                current_race_block = '{}{}'.format(config.heatPrefix, i + 1)
    if heats_started and current_race_block is None:
        current_race_block = config.finalPrefix

    return current_race_block

# define default site data
def getSiteData(id: str = None, user = None):
    menu_teams = {
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
    }

    menu_trainings = {
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
    }

    menu_timetable = {
        'id': 'timetable',
        'title': config.timetableTitle,
        'url': 'timetable',
        'thumb': config.timetableIcon,
        'active': True if id == 'timetable' else False
    }

    menu_times = {
        'id': 'times',
        'title': config.timeTitle,
        'url': 'times',
        'thumb': config.timeIcon,
        'active': True if id == 'times' else False
    }

    menu_results = {
        'id': 'results',
        'title': config.resultsTitle,
        'url': 'results',
        'thumb': config.resultsIcon,
        'active': True if id == 'results' else False
    }

    menu_display = {
        'id': 'display',
        'title': config.displayTitle,
        'url': 'display',
        'thumb': config.displayIcon,
        'active': True if id == 'display' else False
    }
    current_race_block = getCurrentRaceBlock()
    if current_race_block:
        menu_display['notifications'] = [
            {
                'level': 'danger',
                'count': getCurrentRaceBlock()
            }
        ]

    menu_setings = {
        'id': 'settings',
        'title': config.settingsTitle,
        'url': 'settings',
        'thumb': config.settingsIcon,
        'active': True if id == 'settings' else False
    }

    menu_admin = {
        'id': 'djadmin',
        'title': config.adminTitle,
        'url': 'djadmin',
        'thumb': config.adminIcon,
        'active': True if id == 'djadmin' else False
    }

    siteData = {'menu': []}

    if user and user.is_authenticated:
        siteData['menu'].append(menu_teams)
        siteData['menu'].append(menu_trainings)

    siteData['menu'].append(menu_timetable)

    if user and user.is_authenticated:
        siteData['menu'].append(menu_times)

    if config.activateResults or user.is_authenticated:
        siteData['menu'].append(menu_results)

    if user and user.is_authenticated:
        siteData['menu'].append(menu_display)
        siteData['menu'].append(menu_setings)

    if user and user.is_authenticated and user.is_superuser:
        siteData['menu'].append(menu_admin)

    if user and user.is_authenticated:
        siteData['user_name'] = user.username
        siteData['user_fname'] = user.first_name
        siteData['user_lname'] = user.last_name

    return siteData

def getRaceTimes(raceType: str):
    # deduce lane count from database
    lanesPerRace = len(set([attendee.lane for attendee in RaceAssign.objects.all()]))

    races = []
    for race in Race.objects.filter(name__startswith = raceType):
        entry = {
            'time': race.time,
            'desc': race.name,
            'lanes': []
        }

        # get rankings
        attendees = RaceAssign.objects.filter(race_id=race.id).order_by('time')
        rankings = {}
        i = 1
        for attendee in attendees:
            if attendee.time != 0.0:
                rankings[attendee.lane] = i
                i += 1

        # get times table data
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
                        'time': attendee.time,
                        'place': rankings[attendee.lane] if attendee.lane in rankings else '-',
                        'finished': attendee.time != 0.0
                    }
                )
            elif draw:
                entry['lanes'].append(
                    {
                        'lane': draw.lane,
                        'team': draw.desc,
                        'company': '-',
                        'time': None,
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

# Check if selected race block is started
def raceBlockStarted(raceType: str):
    started = False
    for race in Race.objects.filter(name__startswith = raceType):
        attendees = RaceAssign.objects.filter(race_id=race.id).order_by('time')
        for attendee in attendees:
            if attendee.time != 0.0:
                started = True
                break
        if started:
            break
    return started

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
        rankings = {}
        if race:
            # get rankings
            attendees = RaceAssign.objects.filter(race_id=race.id).order_by('time')
            i = 1
            for attendee in attendees:
                if attendee.time != 0.0:
                    rankings[attendee.lane] = i
                    i += 1
        else:
            return {}

        attendees = RaceAssign.objects.filter(race_id=race_id)
        selected_race = {
            'name': race.name,
            'id': race.id,
            'time': race.time,
            'lanes': []
        }
        for attendee in attendees:
            lane = {
                'id': attendee.id,
                'lane': attendee.lane,
                'team': Team.objects.get(id=attendee.team_id).name,
                'place': rankings[attendee.lane] if attendee.lane in rankings else '-',
                'time': attendee.time,
                'finished': attendee.time != 0.0
            }
            selected_race['lanes'].append(lane)
        return selected_race

    controls = {
        'races': [],
        'start_time_icon': 'view-list',
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
            'id': 'durationMonitorSlide',
            'name': config.displayIntervalDesc,
            'type': 'number',
            'value': config.displayInterval / 1e3,
            'icon': 'clock-history'
        },
        {
            'id': 'activateResults',
            'name': config.activateResultsDesc,
            'type': 'checkbox',
            'value': config.activateResults,
            'icon': 'clock-history'
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
