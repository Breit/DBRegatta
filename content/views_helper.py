import os
import re
import math
import json
import shutil
import random

from glob import glob
from datetime import datetime, date, time, timedelta

from constance import config
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.auth import authenticate, login, logout
from django.forms.models import model_to_dict
from django.conf import settings as dj_settings

from .models import Race, RaceAssign, Team, RaceDrawMode, Post, Skipper
from .forms import TeamForm, PostForm, SkipperForm

def loginUser(request, site: str = ''):
    if request.method == "POST":
        log_action= False
        if 'login' in request.POST:
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                login(request, user)
                log_action = True
        elif 'logout' in request.POST:
            logout(request)
            log_action = True

        # revert to default menu fold status
        if log_action:
            if request.user.is_authenticated:
                request.session['fold_menu'] = False
            else:
                request.session['fold_menu'] = True

def toggleFoldMenu(request):
    # handly menu folding
    if 'fold_menu' not in request.session:
        if request.user.is_authenticated:
            request.session['fold_menu'] = False        # default to full menu for auth users
        else:
            request.session['fold_menu'] = True         # default to folded menu for un-auth users (probably mobile users)
    if request.method == 'POST' and 'menu_fold_toggle' in request.POST:
        request.session['fold_menu'] = not request.session['fold_menu']
        return True
    return False

# get teams list from database
def getTeamContent():
    content = { 'teams': [] }

    activeTeams = Team.objects.filter(active=True, wait=False)
    for team in activeTeams:
        content['teams'].append(model_to_dict(team))

    waitingTeams = Team.objects.filter(active=True, wait=True)
    for team in waitingTeams:
        content['teams'].append(model_to_dict(team))

    inactiveTeams = Team.objects.filter(active=False)
    for team in inactiveTeams:
        content['teams'].append(model_to_dict(team))

    content['activeTeams'] = activeTeams.count()
    content['waitlistTeams'] = waitingTeams.count()
    content['inactiveTeams'] = inactiveTeams.count()
    content['totalTeams'] = Team.objects.all().count()
    content['form'] = TeamForm()
    return content

def getSkipperList():
    content = []
    for skipper in Skipper.objects.all():
        content.append(model_to_dict(skipper))
    return content

def combineTimeOffset(t: time, offset: timedelta):
    return (datetime.combine(date.today(), t) + offset).time()

def getTimeTableSettings():
    try:
        post = Post.objects.get(site='timetable')
    except Post.DoesNotExist:
        post = Post()
        post.site = 'timetable'
        post.save()
    post_form = PostForm(instance = post)

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
        },
        {
            'id': 'timetablePost',
            'name': config.placeholderPostContent,
            'type': 'textarea',
            'value': post_form,
            'icon': 'file-richtext'
        }
    ]

    return settings

def getFirstRaceTime(raceType: str):
        race = Race.objects.filter(name__startswith = raceType).order_by('time').first()
        return race.time if race else config.timeBegin

def getLastRaceTime(raceType: str):
        race = Race.objects.filter(name__startswith = raceType).order_by('time').last()
        return race.time if race else config.timeBegin

def getActiveTeams():
    races = Race.objects.filter(name__startswith = config.heatPrefix)
    teams = set([ra.team_id for ra in RaceAssign.objects.filter(race_id__in=races)])
    return len(teams)

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
                try:
                    skipper = Skipper.objects.get(id=attendee.skipper_id)
                    pass
                except:
                    skipper = None
                entry['lanes'].append(
                    {
                        'lane': attendee.lane,
                        'team': team.name,
                        'company': team.company,
                        'skipper': {
                            'name': skipper.name if skipper else '-',
                            'active': skipper.active if skipper else False,
                        },
                        'draw': False
                    }
                )
            elif draw:
                entry['lanes'].append(
                    {
                        'lane': draw.lane,
                        'team': draw.desc,
                        'company': '-',
                        'skipper': {
                            'name': '-',
                            'active': False,
                        },
                        'draw': True
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
    clearRaces()

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
    timetable = []

    # get current heats
    for i in range(config.heatCount):
        races = getRaceTimes('{}{}-'.format(config.heatPrefix, i + 1))
        if len(races) > 0 and all(['lanes' in race for race in races]):
            if all([all(lane['time'] > 0.0 for lane in race['lanes']) for race in races]):
                # current heat already complete
                continue

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
            break

    # get final if heats are finished
    if len(timetable) == 0:
        races = getRaceTimes(config.finalPrefix)

        # distribute too many races over multiple pages
        racesPerPage = len(races)
        pages = 1
        while (racesPerPage > config.maxRacesPerPage):
            racesPerPage = int(math.ceil(float(racesPerPage / 2.0)))
            pages += 1
        for i in range(pages):
            timetable.append(
                {
                    'time': races[0]['time'] if len(races) > 0 else combineTimeOffset(
                        config.timeBegin,
                        config.offsetFinale
                    ),
                    'desc': '{}{}'.format(config.finaleTitle, ' - {} {}'.format(config.racesPerPageDesc, i + 1) if pages > 1 else ''),
                    'races': races[(i * racesPerPage):min((i + 1) * racesPerPage, len(races))],
                    'type': 'finale'
                }
            )

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

def getHeatRankings():
    rankingTable = {
        'desc': '{} {}'.format(config.displayRankings, config.heatsTitle),
        'type':'rankingHeats',
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

# get started/finished status of all heats in the DB
def getHeatsStatus():
    heats_started = []
    heats_finished = []

    # deduce heat count from DB
    heats = Race.objects.filter(name__startswith = config.heatPrefix)
    heatcount = len(set(sum([re.findall(r'{}(\d+)-\d+'.format(config.heatPrefix), heat.name) for heat in heats], [])))

    # get status on all heat races
    for i in range(heatcount):
        heats_started.append([])
        heats_finished.append([])

        heat_races = Race.objects.filter(name__startswith = '{}{}-'.format(config.heatPrefix, i + 1)).order_by('time')
        for race in heat_races:
            assignments = RaceAssign.objects.filter(race_id = race.id)
            heats_started[-1].append(any(assign.time > 0.0 for assign in assignments) and assignments.count() > 0)
            heats_finished[-1].append(all(assign.time > 0.0 for assign in assignments) and assignments.count() > 0)

    return heats_started, heats_finished

# get race names for notifications
#   last    - the last race that has been finished
#   next    - the first occurence of a race that has not been started
#   started - the first race that has been started, but not finished
def getNextRaceName():
    last = None
    next = None
    started = None
    races = Race.objects.all().order_by('time')
    for race in races:
        assignments = RaceAssign.objects.filter(race_id=race.id)
        finished = all([assign.time != 0.0 for assign in assignments]) and assignments.count() > 0
        running = any([assign.time != 0.0 for assign in assignments]) and assignments.count() > 0
        if finished:
            last = race.name
        else:
            if not started and running:
                started = race.name
            elif not next and not running and not finished:
                next = race.name
    return last, next, started

# get current race block (Heat# or Final) for notifications
def getCurrentRaceBlock():
    current_race_block = None
    heats_started, heats_finished = getHeatsStatus()

    # return None if no heat is started at all
    if not any(sum(heats_started, [])):
        return None

    # return finale prefix if all heats are finished
    if all(sum(heats_started, [])) and all(sum(heats_finished, [])):
        return config.finalPrefix

    # figure out which heat is started, but not finished
    for i, (_, finished) in enumerate(zip(heats_started, heats_finished)):
        if all(finished):
            continue
        current_race_block = '{}{}'.format(config.heatPrefix, i + 1)
        break

    return current_race_block

# define default site data
def getSiteData(id: str = None, user = None):
    menu_toggle = {
        'id': 'toggle'
    }
    menu_teams = {
        'id': 'teams',
        'title': config.teamsTitle,
        'url': 'teams',
        'thumb': config.teamsIcon,
        'active': True if id == 'teams' else False,
        'notifications': []
    }
    teams_active = Team.objects.filter(active=True, wait=False).count()
    if teams_active:
        menu_teams['notifications'].append(
            {
                'level': 'success',
                'count': teams_active
            }
        )
    teams_wait = Team.objects.filter(active=True, wait=True).count()
    if teams_active:
        menu_teams['notifications'].append(
            {
                'level': 'warning',
                'count': teams_wait
            }
        )
    teams_inactive = Team.objects.filter(active=False).count()
    if teams_active:
        menu_teams['notifications'].append(
            {
                'level': 'secondary',
                'count': teams_inactive
            }
        )

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

    menu_skippers = {
        'id': 'skippers',
        'title': config.skippersTitle,
        'url': 'skippers',
        'thumb': config.skippersIcon,
        'active': True if id == 'skippers' else False,
        'notifications': []
    }
    skippers_active = Skipper.objects.filter(active=True).count()
    if skippers_active:
        menu_skippers['notifications'].append(
            {
                'level': 'success',
                'count': skippers_active
            }
        )
    skippers_inactive = Skipper.objects.filter(active=False).count()
    if skippers_inactive:
        menu_skippers['notifications'].append(
            {
                'level': 'secondary',
                'count': skippers_inactive
            }
        )

    menu_timetable = {
        'id': 'timetable',
        'title': config.timetableTitle,
        'url': 'timetable',
        'thumb': config.timetableIcon,
        'active': True if id == 'timetable' else False,
        'notifications': []
    }

    menu_times = {
        'id': 'times',
        'title': config.timeTitle,
        'url': 'times',
        'thumb': config.timeIcon,
        'active': True if id == 'times' else False,
        'notifications': []
    }
    last, next, started = getNextRaceName()
    if started is not None:
        menu_times['notifications'].append(
            {
                'level': 'warning',
                'count': started
            }
        )
    elif last is not None:
        menu_times['notifications'].append(
            {
                'level': 'success',
                'count': last
            }
        )
    if next is not None:
        menu_times['notifications'].append(
            {
                'level': 'danger',
                'count': next
            }
        )

    menu_results = {
        'id': 'results',
        'title': config.resultsTitle,
        'url': 'results',
        'thumb': config.resultsIcon,
        'active': True if id == 'results' else False,
        'notifications': []
    }

    menu_display = {
        'id': 'display',
        'title': config.displayTitle,
        'url': 'display',
        'thumb': config.displayIcon,
        'active': True if id == 'display' else False,
        'notifications': []
    }
    current_race_block = getCurrentRaceBlock()
    if current_race_block:
        menu_display['notifications'] = [
            {
                'level': 'danger',
                'count': getCurrentRaceBlock()
            }
        ]

    menu_settings = {
        'id': 'settings',
        'title': config.settingsTitle,
        'url': 'settings',
        'thumb': config.settingsIcon,
        'active': True if id == 'settings' else False,
        'notifications': []
    }

    menu_admin = {
        'id': 'djadmin',
        'title': config.adminTitle,
        'url': 'djadmin',
        'thumb': config.adminIcon,
        'active': True if id == 'djadmin' else False,
        'notifications': []
    }

    siteData = {
        'menu': [],
        'impressum': '/impressum'
    }

    if user and user.is_authenticated:
        siteData['menu'].append(menu_teams)
        siteData['menu'].append(menu_skippers)
        siteData['menu'].append(menu_trainings)

    siteData['menu'].append(menu_timetable)

    if user and user.is_authenticated:
        siteData['menu'].append(menu_times)

    if config.activateResults or user.is_authenticated:
        siteData['menu'].append(menu_results)

    if user and user.is_authenticated:
        siteData['menu'].append(menu_display)

    siteData['menu'].append(menu_toggle)

    if user and user.is_authenticated:
        siteData['menu'].append(menu_settings)

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

    # get all final races and sort after race names, but obey number ordering
    races_sorted = Race.objects.filter(name__startswith = raceType)
    races_sorted = [race for race in races_sorted]
    races_sorted.sort(key=lambda x:[int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x.name)])

    races = []
    if raceType == config.finalPrefix:
        rank_finale = getActiveTeams()

    for race in races_sorted:
        entry = {
            'time': race.time,
            'desc': race.name,
            'lanes': []
        }

        # get rankings
        attendees = RaceAssign.objects.filter(race_id=race.id).order_by('time')
        rankings = {}
        for i, attendee in enumerate(attendees):
            if attendee.time != 0.0:
                rankings[attendee.lane] = i + 1

        # get times table data
        for lnum in range(lanesPerRace):
            try:
                attendee = RaceAssign.objects.get(race_id=race.id, lane=(lnum + 1))
                team = Team.objects.get(id=attendee.team_id)
            except MultipleObjectsReturned:
                attendee = RaceAssign.objects.filter(race_id=race.id, lane=(lnum + 1))[0]
            except ObjectDoesNotExist:
                attendee = None
                team = None
            try:
                draw = RaceDrawMode.objects.get(race_id=race.id, lane=(lnum + 1))
            except ObjectDoesNotExist:
                draw = None
            if team:
                try:
                    skipper = Skipper.objects.get(id=attendee.skipper_id)
                except:
                    skipper = None
                entry['lanes'].append(
                    {
                        'lane': attendee.lane,
                        'team': team.name,
                        'company': team.company,
                        'time': attendee.time,
                        'skipper': {
                            'name': skipper.name if skipper else '-',
                            'active': skipper.active if skipper else False,
                        },
                        'place': rankings[attendee.lane] if attendee.lane in rankings else '-',
                        'finished': attendee.time != 0.0,
                        'draw': False
                    }
                )
            elif draw:
                entry['lanes'].append(
                    {
                        'lane': draw.lane,
                        'team': draw.desc,
                        'company': '-',
                        'time': None,
                        'skipper': {
                            'name': '-',
                            'active': False
                        },
                        'place': '-',
                        'finished': False,
                        'draw': True
                    }
                )

        # fill in ranks for finale
        if raceType == config.finalPrefix:
            lanesInRace = len(entry['lanes']) if len(entry['lanes']) > 0 else lanesPerRace
            if len([lane for lane in entry['lanes'] if lane['finished']]) == lanesInRace:
                last_race = race.name == races_sorted[-1].name
                for lane in entry['lanes']:
                    if not last_race and lane['place'] == 1:
                        continue
                    lane['rank'] = rank_finale - (lanesInRace - lane['place'])
                rank_finale -= lanesInRace if last_race else lanesInRace - 1

        if all(item['finished'] for item in entry['lanes']):
            entry['status'] = 'finished'
        elif any(item['finished'] for item in entry['lanes']):
            entry['status'] = 'started'
        else:
            entry['status'] = 'not_started'
        races.append(entry)
    return races

def getFinalRankings():
    rankingTable = {
        'desc': '{} {}'.format(config.displayRankings, config.finaleTitle),
        'ranks': [],
        'type': 'rankingFinals'
    }

    # deduce lane count from database
    lanesPerRace = len(set([attendee.lane for attendee in RaceAssign.objects.all()]))

    # get all final races and sort after race names, but obey number ordering
    races_sorted = Race.objects.filter(name__startswith = config.finalPrefix)
    races_sorted = [race for race in races_sorted]
    races_sorted.sort(key=lambda x:[int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x.name)])

    rank_finale = getActiveTeams()

    for race in races_sorted:
        entry = {
            'time': race.time,
            'desc': race.name,
            'lanes': []
        }

        # get rankings
        attendees = RaceAssign.objects.filter(race_id=race.id).order_by('time')
        placings = {}
        for i, attendee in enumerate(attendees):
            if attendee.time != 0.0:
                placings[attendee.lane] = i + 1

        # get times table data
        for lnum in range(lanesPerRace):
            try:
                attendee = RaceAssign.objects.get(race_id=race.id, lane=(lnum + 1))
                team = Team.objects.get(id=attendee.team_id)
            except MultipleObjectsReturned:
                attendee = RaceAssign.objects.filter(race_id=race.id, lane=(lnum + 1))[0]
            except ObjectDoesNotExist:
                attendee = None
                team = None
            if team and attendee:
                entry['lanes'].append(
                    {
                        'team': team,
                        'time': attendee.time,
                        'place': placings[attendee.lane] if attendee.lane in placings else '-',
                        'finished': attendee.time != 0.0
                    }
                )

        # fill in ranks for finale
        lanesInRace = len(entry['lanes']) if len(entry['lanes']) > 0 else lanesPerRace
        if len([lane for lane in entry['lanes'] if lane['finished']]) == lanesInRace:
            last_race = race.name == races_sorted[-1].name
            for lane in entry['lanes']:
                if not last_race and lane['place'] == 1:
                    continue

                assignments_finals = RaceAssign.objects.filter(
                    team_id = lane['team'].id,
                    race_id__in = [r.id for r in races_sorted]
                ).order_by('time')

                races_heats = Race.objects.filter(name__startswith = config.heatPrefix)
                assignments_heats = RaceAssign.objects.filter(
                    team_id = lane['team'].id,
                    race_id__in = [r.id for r in races_heats]
                ).order_by('time')

                rankingTable['ranks'].append(
                    {
                        'rank': rank_finale - (lanesInRace - lane['place']),
                        'team': lane['team'].name,
                        'company': lane['team'].company,
                        'bt_heats': assignments_heats.first().time if assignments_heats.count() else None,
                        'bt_finale': assignments_finals.first().time if assignments_finals.count() else None,
                        'finale_time': lane['time'],
                        'races': assignments_finals.count(),
                    }
                )
            rank_finale -= lanesInRace if last_race else lanesInRace - 1

        # sort rankings
        rankingTable['ranks'].sort(key=lambda r: r['rank'])

    return rankingTable

# Check if selected race block is started
def raceBlockStarted(raceType: str):
    started = False
    for race in Race.objects.filter(name__startswith = raceType):
        attendees = RaceAssign.objects.filter(race_id=race.id)
        if any([attendee.time > 0.0 for attendee in attendees]) and len(attendees) > 0:
            started = True
            break
    return started

# Check if selected race block is finished
def raceBlockFinished(raceType: str):
    finished = []
    for race in Race.objects.filter(name__startswith = raceType):
        attendees = RaceAssign.objects.filter(race_id=race.id)
        if all([attendee.time > 0.0 for attendee in attendees]) and len(attendees) > 0:
            finished.append(True)
        else:
            finished.append(False)
    return all(finished)

def getRaceResultsTableContent(heats: bool = True, heatsRankings: bool = True, finals: bool = True, finalRanks: bool = True):
    timetable = []

    # heats results
    if heats:
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

    # get heat rankings
    if heatsRankings:
        races = Race.objects.filter(name__startswith = config.heatPrefix).order_by('time')
        if len(races) > 0:
            timetable.append(getHeatRankings())
            timetable[-1]['time'] = races.last().time

    # finals results
    if finals:
        if len(timetable) > 0:
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

    # finals rankings
    if finalRanks:
        timetable.append(getFinalRankings())

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

        attendees = RaceAssign.objects.filter(race_id=race_id).order_by('lane')
        selected_race = {
            'name': race.name,
            'id': race.id,
            'time': race.time,
            'lanes': []
        }
        for attendee in attendees:
            try:
                skipper = Skipper.objects.get(id=attendee.skipper_id)
            except:
                skipper = None
            lane = {
                'id': attendee.id,
                'lane': attendee.lane,
                'team': Team.objects.get(id=attendee.team_id).name,
                'skipper': {
                    'name': skipper.name if skipper else '-',
                    'active': skipper.active if skipper else False
                },
                'place': rankings[attendee.lane] if attendee.lane in rankings else '-',
                'time': attendee.time,
                'finished': attendee.time != 0.0
            }
            selected_race['lanes'].append(lane)
        return selected_race

    controls = {
        'races': [''],
        'skippers': [''],
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

    skippers = Skipper.objects.all()
    for skipper in skippers:
        controls['skippers'].append(
            {
                'name': skipper.name,
                'active': skipper.active
            }
        )

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
            'id': 'displayOverscan',
            'name': config.overscanDesc,
            'type': 'number',
            'value': config.overscan,
            'icon': 'aspect-ratio',
            'min': 0,
            'max': config.overscanMax
        },
        {
            'id': 'durationMonitorSlide',
            'name': config.displayIntervalDesc,
            'type': 'number',
            'value': int(config.displayInterval / 1e3),
            'icon': 'clock-history'
        },
        {
            'id': 'displayDataRefresh',
            'name': config.displayDataRefreshDesc,
            'type': 'number',
            'value': int(config.displayDataRefresh / 1e3),
            'icon': 'clock-history'
        },
        {
            'id': 'maxRacesPerPage',
            'name': config.maxRacesPerPageDesc,
            'type': 'number',
            'value': config.maxRacesPerPage,
            'icon': 'file-ruled'
        },
        {
            'id': 'activateResults',
            'name': config.activateResultsDesc,
            'type': 'checkbox',
            'value': config.activateResults,
            'icon': 'clock-history'
        },
        {
            'id': 'anonymousMonitor',
            'name': config.anonymousMonitorDesc,
            'type': 'checkbox',
            'value': config.anonymousMonitor,
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
            'type': 'url',
            'value': config.ownerUrl,
            'icon': 'link-45deg'
        },
        {
            'id': 'sponsorUrl',
            'name': config.sponsorUrlDesc,
            'type': 'url',
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
        },
        {
            'id': 'liveResultsHint',
            'name': config.liveResultsHintDesc,
            'type': 'text',
            'value': config.liveResultsHint,
            'icon': 'info-square'
        },
        {
            'id': 'siteDomain',
            'name': config.liveResultsDomainDesc,
            'type': 'text',
            'value': config.domain,
            'icon': 'link'
        }
    ]

    return settings

# check if all heats are finished and if so, create rankings and fill finals
def populateFinals(race_assignment: RaceAssign = None):
    if getCurrentRaceBlock() == config.finalPrefix:
        # get all final races and sort after race names in reverse order, but obey number ordering
        races = Race.objects.filter(name__startswith = config.finalPrefix)
        races_sorted = [(race.id, race.name) for race in races]
        races_sorted.sort(key=lambda x:[int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x[1])], reverse=True)
        race_ids = [race[0] for race in races_sorted]

        # for already running finals, decide if a winner from a particular final race can ascend one race
        if race_assignment:
            assignee_race = Race.objects.get(id = race_assignment.race_id)
            if assignee_race.name.startswith(config.finalPrefix):
                attendees = RaceAssign.objects.filter(race_id=assignee_race.id).order_by('time')
                if all([attendee.time > 0.0 for attendee in attendees]):
                    # find next race
                    if assignee_race.id in race_ids:
                        race_idx = race_ids.index(assignee_race.id)
                        if race_idx > 0:
                            # attendees[0] holds the winner, ascend him to the next race
                            ra = None
                            try:
                                # check if there is already an assignment (due to race time changes)
                                ra = RaceAssign.objects.get(race_id=race_ids[race_idx - 1], lane=1)
                            except:
                                ra = RaceAssign()   # create a new assignment
                                ra.lane = 1         # winner starts on lane #1

                            ra.race_id = race_ids[race_idx - 1]
                            if ra.team_id != attendees[0].team_id:
                                ra.time = 0.0
                                ra.team_id = attendees[0].team_id
                                ra.save()

                                # Draw is changed: Remove winning team from next race
                                # and correct timetable recursively
                                for idx in reversed(range(race_idx)):
                                    try:
                                        ras = RaceAssign.objects.filter(race_id=race_ids[idx])
                                        for ra in ras:
                                            if idx < (race_idx - 1) and ra.lane == 1:
                                                ra.delete()         # remove winner from previous race, because previous race is undecided now
                                            else:
                                                ra.time = 0.0       # remove race times from other contenders
                                                ra.save()
                                    except:
                                        pass

        # create all race assignments for the finals if necessary
        # fill rankings to finals
        # TODO: If a heat race gets modified, decide if the finals should be re-populated based on rankings from heats!
        attendees = RaceAssign.objects.filter(race_id__in=race_ids)
        if len(attendees) == 0:
            rankings = getRankings()
            if len(rankings) > 0:
                rank_id = 0
                for race_id in race_ids:
                    for lane in reversed(range(config.lanesPerRace)):
                        if rank_id >= len(rankings):
                            break
                        if race_id != race_ids[-1] and lane == 0 or lane + 1 > len(rankings) - rank_id:
                            # leave lane free for winner from previous race
                            continue
                        ra = RaceAssign()
                        ra.race_id = race_id
                        ra.lane = lane + 1
                        ra.team_id = rankings[rank_id]['team_id']
                        ra.save()
                        rank_id += 1

# CAUTION: Developer Tools !!!
# remove all finals including racing times from the DB
def clearFinals():
    # get race IDs for finale races
    races = Race.objects.filter(name__startswith = config.finalPrefix)
    race_ids = [race.id for race in races]

    # delete all finale assignments
    RaceAssign.objects.filter(race_id__in=race_ids).delete()

# remove all heats including racing times from the DB including finals and race assignments
def clearRaces():
    # delete all race assignments for the heats
    RaceAssign.objects.all().delete()

    # delete all race draw modes
    RaceDrawMode.objects.all().delete()

    # remove all races
    Race.objects.all().delete()

# remove all heat racing times from the DB and clear all finals
def clearHeatTimes():
    clearFinals()
    races = Race.objects.filter(name__startswith = config.heatPrefix)
    race_ids = [race.id for race in races]
    attendees = RaceAssign.objects.filter(race_id__in=race_ids)
    if len(attendees) > 0:
        for attendee in attendees:
            attendee.time = 0.0
            attendee.skipper_id = None
            attendee.save()

def backupDataBase():
    try:
        db_fname = '{}_{}'.format(
            datetime.now().strftime('%Y%m%d-%H%M%S'),
            os.path.basename(dj_settings.DATABASES['default']['NAME'])
        )

        shutil.copyfile(
            dj_settings.DATABASES['default']['NAME'],
            os.path.join(dj_settings.DATABASE_BACKUP_DIR, db_fname)
        )
        success = True
    except:
        success = False
    return success

def getLastDataBaseBackup():
    base_name = os.path.basename(dj_settings.DATABASES['default']['NAME'])
    backups = glob(os.path.join(dj_settings.DATABASE_BACKUP_DIR, '*_' + base_name))
    backups.sort(key=lambda x:[int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
    if len(backups) > 0:
        date_str = os.path.basename(backups[-1]).replace(base_name, '')
        try:
            return datetime.strptime(date_str, '%Y%m%d-%H%M%S_').strftime('%Y.%m.%d %H:%M:%S')
        except:
            pass
    return None

def getImpressumData():
    impressum = None
    try:
        with open(os.path.join(dj_settings.STATIC_ROOT, 'data', 'impressum.json'), encoding='utf-8') as impressum_json:
            impressum = json.load(impressum_json)
    except:
        pass
    return impressum

def clearSkippers():
    # clear all skippers from race assignments
    assignments = RaceAssign.objects.all()
    for assignment in assignments:
        assignment.skipper_id = None
        assignment.save()

    # empty skipper DB
    Skipper.objects.all().delete()

def clearTeams():
    # clear all heats and finals including race assignments
    clearRaces()

    # empty team DB
    Team.objects.all().delete()
