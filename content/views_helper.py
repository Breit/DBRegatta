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
from django.db.models import F, Q

from .models import Race, RaceAssign, Team, RaceDrawMode, Post, Skipper, Training
from .forms import TeamForm, PostForm, SkipperForm, TrainingForm

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

    activeTeams = Team.objects.filter(active=True, wait=False).order_by(F('position').asc(nulls_last=True))
    for team in activeTeams:
        content['teams'].append(model_to_dict(team))

    waitingTeams = Team.objects.filter(active=True, wait=True).order_by(F('position').asc(nulls_last=True))
    for team in waitingTeams:
        content['teams'].append(model_to_dict(team))

    inactiveTeams = Team.objects.filter(active=False).order_by(F('position').asc(nulls_last=True))
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

def getSkipperContent():
    content = {
        'skipperList': getSkipperList(),
        'activeSkippers': Skipper.objects.filter(active = True).count(),
        'inactiveSkippers': Skipper.objects.filter(active = False).count(),
        'skipperForm': SkipperForm()
    }

    return content

def getTrainingsList(active=True, upcomingOnly=False, pastOnly=False):
    content = []
    now = datetime.now()
    date_now = now.date()
    time_now = now.time()
    if upcomingOnly:
        trainings = Training.objects.filter(active=active).filter(
            Q(date__gt=date_now) | Q(date=date_now, time__gt=time_now)
        ).order_by('date', 'time')
    elif pastOnly:
        trainings = Training.objects.filter(active=active).filter(
            Q(date__lt=date_now) | Q(date=date_now, time__lt=time_now)
        ).order_by('date', 'time')
    else:
        trainings = Training.objects.filter(active=active)

    for training in trainings:
        entry = {}
        entry['id'] = training.pk
        entry['date'] = training.date
        entry['time_start'] = training.time
        entry['time_end'] = (datetime.combine(date.today(), training.time) + training.duration).time()
        entry['notes'] = training.notes

        team = Team.objects.get(id=training.team_id)
        entry['team'] = {}
        entry['team']['id'] = training.team_id
        entry['team']['name'] = team.name
        entry['team']['company'] = team.company
        entry['team']['contact'] = team.contact
        entry['team']['email'] = team.email
        entry['team']['phone'] = team.phone

        skipper = Skipper.objects.get(id=training.skipper_id)
        entry['skipper'] = {}
        entry['skipper']['id'] = training.skipper_id
        entry['skipper']['name'] = skipper.name
        entry['skipper']['fname'] = skipper.fname
        entry['skipper']['lname'] = skipper.lname
        entry['skipper']['email'] = skipper.email

        content.append(entry)
    return content

def getTrainingsContent():
    availableSkippers = Skipper.objects.filter(active=True)
    availableTeams = Team.objects.filter(active=True, wait=False)

    content = {
        'trainingsList': {
            'upcoming': getTrainingsList(upcomingOnly=True),
            'past': getTrainingsList(pastOnly=True),
            'inactive': getTrainingsList(active=False)
        },
        'countTrainings': Training.objects.all().count(),
        'countTeams': availableTeams.count(),
        'countSkippers': availableSkippers.count(),
        'availableTeams': [model_to_dict(team) for team in availableTeams],
        'availableSkippers': [model_to_dict(skipper) for skipper in availableSkippers],
        'timeSuggestions': [],
        'trainingsStats': [],
        'form': TrainingForm()
    }

    # Generate team stats
    now = datetime.now()
    date_now = now.date()
    time_now = now.time()

    teamStats = {
        'type': 'team',
        'header': config.statsTrainingsPerTeam,
        'table_header': {
            'id': config.trainingsTableHeaderID,
            'name': config.teamTableHeaderTeam + ' / ' + config.teamTableHeaderCompany,
            'stat': config.trainingsTrainings,
            'total': config.trainingsCountTrainings
        },
        'stats': [],
        'maxTrainings': 0
    }
    for team in availableTeams:
        trainings = Training.objects.filter(team_id=team.id).count()
        if trainings > 0:
            team_dict = model_to_dict(team)
            team_dict['subname'] = team_dict.pop('company')
            team_dict['totalTrainings'] = trainings
            team_dict['upcomingTrainings'] = Training.objects \
                .filter(team_id=team.id, active=True) \
                .filter(Q(date__gt=date_now) | Q(date=date_now, time__gt=time_now)) \
                .count()
            team_dict['pastTrainings'] = Training.objects \
                .filter(team_id=team.id, active=True) \
                .filter(Q(date__lt=date_now) | Q(date=date_now, time__lt=time_now)) \
                .count()
            team_dict['inactiveTrainings'] = Training.objects \
                .filter(team_id=team.id, active=False) \
                .count()
            teamStats['stats'].append(team_dict)
            teamStats['maxTrainings'] = max(teamStats['maxTrainings'], team_dict['totalTrainings'])
    teamStats['stats'] = sorted(teamStats['stats'], key=lambda d: d['totalTrainings'], reverse=True)      # sort
    content['trainingsStats'].append(teamStats)

    skipperStats = {
        'type': 'skipper',
        'header': config.statsTrainingsPerSkipper,
        'table_header': {
            'id': config.trainingsTableHeaderID,
            'name': config.skipper,
            'stat': config.trainingsTrainings,
            'total': config.trainingsCountTrainings
        },
        'stats': [],
        'maxTrainings': 0
    }
    for skipper in availableSkippers:
        trainings = Training.objects.filter(skipper_id=skipper.id).count()
        if trainings > 0:
            skipper_dict = model_to_dict(skipper)
            skipper_dict['subname'] = skipper_dict.pop('email')
            skipper_dict['totalTrainings'] = trainings
            skipper_dict['upcomingTrainings'] = Training.objects \
                .filter(skipper_id=skipper.id, active=True) \
                .filter(Q(date__gt=date_now) | Q(date=date_now, time__gt=time_now)) \
                .count()
            skipper_dict['pastTrainings'] = Training.objects \
                .filter(skipper_id=skipper.id, active=True) \
                .filter(Q(date__lt=date_now) | Q(date=date_now, time__lt=time_now)) \
                .count()
            skipper_dict['inactiveTrainings'] = Training.objects \
                .filter(skipper_id=skipper.id, active=False) \
                .count()
            skipperStats['stats'].append(skipper_dict)
            skipperStats['maxTrainings'] = max(skipperStats['maxTrainings'], skipper_dict['totalTrainings'])
    skipperStats['stats'] = sorted(skipperStats['stats'], key=lambda d: d['totalTrainings'], reverse=True)      # sort
    content['trainingsStats'].append(skipperStats)

    # Generate training possible start times
    startTime = config.firstTrainingTime
    while startTime <= config.lastTrainingTime:
        content['timeSuggestions'].append(startTime.strftime('%H:%M'))
        startTime = (datetime.combine(date.today(), startTime) + config.intervalTrainingBegin).time()

    return content

def getBillingContent():
    content = {
        'sumCompensations': 0,
        'sumFees': 0,
        'tables': []
    }

    # Add billing data for skippers
    skippersContent = {
        'type': 'skippers',
        'header': config.skippersListHeading,
        'id': 'billing_skipper',
        'data': []
    }
    availableSkippers = Skipper.objects.all()
    for skipper in availableSkippers:
        try:
            skipperTrainings = Training.objects.filter(skipper_id=skipper.id)
        except:
            continue

        data = {}
        data['row'] = [
            {
                'name': config.skipperTableHeaderID,
                'data': skipper.id,
                'columnClasses': 'col col-1 id_col text-center',
                'contentClasses': 'fw-bold text-primary'
            },
            {
                'name': config.placeholderSkipperFName,
                'data': skipper.fname,
                'columnClasses': 'col col-md-3 col-lg-2',
                'contentClasses': 'fw-bold'
            },
            {
                'name': config.placeholderSkipperLName,
                'data': skipper.lname,
                'columnClasses': 'col col-lg-2',
                'contentClasses': 'fw-bold'
            },
            {
                'type': 'email',
                'name': config.placeholderSkipperEmail,
                'data': skipper.email,
                'columnClasses': 'col d-none d-lg-block',
                'contentClasses': ''
            },
            {
                'name': config.trainingsTrainings,
                'data': skipperTrainings.count(),
                'columnClasses': 'col col-1 trainings_col d-none d-md-block text-center',
                'contentClasses': ''
            },
            {
                'name': config.headerCompensation,
                'data': '{value} {currency}'.format(
                    value=skipperTrainings.count() * config.skipperTrainingsCompensation,
                    currency=config.currency
                ),
                'columnClasses': 'col col-1 money_col text-end',
                'contentClasses': 'fw-bold text-success'
            }
        ]
        data['subtable'] = {
            'id': skipper.id,
            'type': 'training',
            'header': config.headerIndividualEntries,
            'data': []
        }
        content['sumCompensations'] += skipperTrainings.count() * config.skipperTrainingsCompensation

        for training in skipperTrainings:
            try:
                team = Team.objects.get(id=training.team_id)
            except:
                continue
            entry = [
                {
                    'name': config.trainingsTableHeaderID,
                    'data': training.id,
                    'columnClasses': 'col col-1 id_col small text-center',
                    'contentClasses': ''
                },
                {
                    'name': config.placeholderTrainingDate,
                    'data': training.date.strftime('%d. %B %Y'),
                    'columnClasses': 'col date_col small',
                    'contentClasses': 'fw-bold text-primary'
                },
                {
                    'name': config.placeholderTrainingTime,
                    'data': '{start} - {end} {timeSuffix}'.format(
                        start=training.time.strftime('%H:%M'),
                        end=(datetime.combine(date.today(), training.time) + training.duration).time().strftime('%H:%M'),
                        timeSuffix=config.timeSuffix
                    ),
                    'columnClasses': 'col time_col small',
                    'contentClasses': ''
                },
                {
                    'name': config.teamTableHeaderTeam,
                    'data': team.name,
                    'columnClasses': 'col col-xl-2 small',
                    'contentClasses': 'fw-bold text-primary'
                },
                {
                    'name': config.teamTableHeaderCompany,
                    'data': team.company,
                    'columnClasses': 'col d-none d-xl-block small',
                    'contentClasses': ''
                },
                {
                    'name': config.placeholderTrainingNotes,
                    'data': training.notes,
                    'columnClasses': 'col d-none d-xxl-block small',
                    'contentClasses': ''
                },
                {
                    'name': config.headerCompensation,
                    'data': '{value} {currency}'.format(
                        value=config.skipperTrainingsCompensation,
                        currency=config.currency
                    ),
                    'columnClasses': 'col col-1 money_col text-end small',
                    'contentClasses': 'fw-bold text-success'
                }
            ]
            data['subtable']['data'].append(entry)

        if len(data['subtable']['data']) <= 0:
            continue

        skippersContent['data'].append(data)

    if len(skippersContent['data']) > 0:
        content['tables'].append(skippersContent)

    # Add billing data for teams
    teamsContent = {
        'type': 'teams',
        'header': config.teamListHeader,
        'id': 'billing_teams',
        'data': []
    }
    availableTeams = Team.objects.all()
    for team in availableTeams:
        teamTrainings = []
        try:
            teamTrainings = Training.objects.filter(team_id=team.id)
        except:
            pass

        if len(teamTrainings) == 0 and not team.active and team.wait:
            continue

        # Add teams that participate in the event and/or had booked a training
        fee_sum = 0
        data = {}

        data['subtable'] = {
            'id': team.id,
            'type': 'training',
            'header': config.headerIndividualEntries,
            'data': []
        }

        # Booked trainings
        for n, training in enumerate(teamTrainings):
            try:
                skipper = Skipper.objects.get(id=training.skipper_id)
            except:
                continue

            # First training is usually included in event fee, but only if the team participates in the event.
            # In case the team is on the waitlist or inactive, it does not participate in the event and thus
            # has to pay for all booked trainings.
            fee = 0 if config.firstTrainingIsFree and n == 0 and team.active and not team.wait else config.trainingsFee
            entry = [
                {
                    'name': config.trainingsTableHeaderID,
                    'data': training.id,
                    'columnClasses': 'col col-1 id_col small text-center',
                    'contentClasses': ''
                },
                {
                    'name': config.placeholderTrainingDate,
                    'data': training.date.strftime('%d. %B %Y'),
                    'columnClasses': 'col date_col small',
                    'contentClasses': 'fw-bold text-primary'
                },
                {
                    'name': config.placeholderTrainingTime,
                    'data': '{start} - {end} {timeSuffix}'.format(
                        start=training.time.strftime('%H:%M'),
                        end=(datetime.combine(date.today(), training.time) + training.duration).time().strftime('%H:%M'),
                        timeSuffix=config.timeSuffix
                    ),
                    'columnClasses': 'col d-none d-lg-block time_col small',
                    'contentClasses': ''
                },
                {
                    'name': config.skipper,
                    'data': '{fname} {lname}'.format(
                        fname=skipper.fname,
                        lname=skipper.lname
                    ),
                    'columnClasses': 'col col-xl-2 small',
                    'contentClasses': 'fw-bold text-primary'
                },
                {
                    'type': 'email',
                    'name': config.placeholderSkipperEmail,
                    'data': skipper.email,
                    'columnClasses': 'col d-none d-xl-block small',
                    'contentClasses': ''
                },
                {
                    'name': config.placeholderTrainingNotes,
                    'data': training.notes,
                    'columnClasses': 'col d-none d-xxl-block small',
                    'contentClasses': ''
                },
                {
                    'name': config.headerFee,
                    'data': '{value} {currency}'.format(
                        value=fee,
                        currency=config.currency
                    ),
                    'columnClasses': 'col col-1 money_col text-end small',
                    'contentClasses': 'fw-bold text-success'
                }
            ]
            data['subtable']['data'].append(entry)
            fee_sum += fee

        # Event participation
        if team.active and not team.wait:
            # Sponsoring teams usually get the event for free
            fee = 0 if team.nofee else config.eventFee
            entry = [
                {
                    'name': config.trainingsTableHeaderID,
                    'data': config.racedayTag,
                    'columnClasses': 'col col-1 id_col small text-center',
                    'contentClasses': ''
                },
                {
                    'name': config.eventDateDesc,
                    'data': config.eventDate.strftime('%d. %B %Y'),
                    'columnClasses': 'col date_col small',
                    'contentClasses': 'fw-bold text-primary'
                },
                {
                    'name': config.siteNameDesc,
                    'data': config.siteName,
                    'columnClasses': 'col small text-center',
                    'contentClasses': 'fw-bold text-danger'
                },
                {
                    'name': config.headerFee,
                    'data': '{value} {currency}'.format(
                        value=fee,
                        currency=config.currency
                    ),
                    'columnClasses': 'col col-1 money_col text-end small',
                    'contentClasses': 'fw-bold text-success'
                }
            ]
            data['subtable']['data'].append(entry)
            fee_sum += fee

        # Main row definition for each participating team
        if len(data['subtable']['data']) > 0:
            data['row'] = [
                {
                    'name': config.teamTableHeaderID,
                    'data': team.id,
                    'columnClasses': 'col col-1 id_col text-center',
                    'contentClasses': 'fw-bold text-primary'
                },
                {
                    'name': config.teamTableHeaderTeam,
                    'data': team.name,
                    'columnClasses': 'col col-md-3 col-lg-2',
                    'contentClasses': 'fw-bold'
                },
                {
                    'name': config.teamTableHeaderCompany,
                    'data': team.company,
                    'columnClasses': 'col d-none d-lg-block small',
                    'contentClasses': ''
                },
                {
                    'name': config.teamTableHeaderCaptain,
                    'data': team.contact,
                    'columnClasses': 'col col-xl-2',
                    'contentClasses': 'fw-bold'
                },
                {
                    'type': 'email',
                    'name': config.teamTableHeaderEmail,
                    'data': team.email,
                    'columnClasses': 'col d-none d-xl-block',
                    'contentClasses': ''
                },
                {
                    'name': config.headerFee,
                    'data': '{value} {currency}'.format(
                        value=fee_sum,
                        currency=config.currency
                    ),
                    'columnClasses': 'col col-1 money_col text-end',
                    'contentClasses': 'fw-bold text-success'
                }
            ]

            teamsContent['data'].append(data)
            content['sumFees'] += fee_sum

    if len(teamsContent['data']) > 0:
        content['tables'].append(teamsContent)

    return content

def getCalendarData(authenticated: bool = False):
    content = []

    noEvents = {
        'events': [
            {
                'start' : config.registrationDate.strftime('%Y-%m-%d'),
                'end' : (config.eventDate + timedelta(days=1)).strftime('%Y-%m-%d'),
                'allDay' : True,
                'display' : 'inverse-background',
                'className' : 'bg-danger no-activity'
            }
        ],
        'className' : 'text-light no-events'
    }
    content.append(noEvents)

    raceday = {
        'events': [
            {
                'title' : config.siteName,
                'start' : config.eventDate.strftime('%Y-%m-%d'),
                'allDay' : True,
                'display' : 'background',
                'className' : 'bg-danger raceday'
            },
            {
                'title' : config.registrationDateDesc,
                'start' : config.registrationDate.strftime('%Y-%m-%d'),
                'allDay' : True,
                'display' : 'background',
                'className' : 'bg-success raceday'
            }
        ],
        'className' : 'text-light no-activity'
    }
    content.append(raceday)

    trainingEvents = {
        'events': [],
        'className' : 'bg-primary text-light'
    }
    trainings = Training.objects.all()
    for training in trainings:
        name = config.appointmentPlaceholder
        skipper = None
        company = None
        note = None
        if authenticated:
            team_obj = Team.objects.get(id=training.team_id)
            if team_obj:
                name = team_obj.name
                company = team_obj.company
            note = training.notes

        skipper_obj = Skipper.objects.get(id=training.skipper_id)
        if skipper_obj:
            skipper = skipper_obj.name

        event = {
            'title': name,
            'start': datetime.combine(training.date, training.time).strftime('%Y-%m-%dT%H:%M'),
            'end': (datetime.combine(training.date, training.time) + training.duration).strftime('%Y-%m-%dT%H:%M'),
            'className': 'training',
            'extendedProps': {
                'skipper': skipper,
                'company': company,
                'note': note,
                'timeslot':
                    datetime.combine(training.date, training.time).strftime('%H:%M') +
                    ' ' +
                    config.timeSuffix +
                    ' - ' +
                    (datetime.combine(training.date, training.time) + training.duration).strftime('%H:%M') +
                    ' ' +
                    config.timeSuffix
            }
        }
        trainingEvents['events'].append(event)
    content.append(trainingEvents)

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

    settings = {
        'id': 'timetablePost',
        'name': config.placeholderPostContent,
        'type': 'textarea',
        'value': post_form,
        'icon': 'file-richtext'
    }

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
            'boarding': combineTimeOffset(race.time, -config.boardingTime),
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
    finale_races = getRaces(config.finalPrefix)
    if (len(finale_races) > 0):
        timetable.append(
            {
                'time': combineTimeOffset(
                    timetable[-1]['races'][-1]['time']
                        if 'races' in timetable[-1] and len(timetable[-1]['races']) > 0
                        else timetable[-1]['time'],
                    config.offsetFinale
                ),
                'desc': config.finaleTitle,
                'races': finale_races,
                'type': 'finale',
                'fold': getCurrentRaceBlock() != config.finalPrefix
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
    if teams.count() == 0:
        return

    teams_idx = list(range(teams.count()))
    lastHeat = []
    for hnum in range(config.heatCount):
        lane = 0
        rnum = 0
        random.shuffle(teams_idx)

        # add heat intermission
        if hnum > 0:
            start = combineTimeOffset(start, config.intermissionHeat)

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
    if 'race' in locals():
        start = combineTimeOffset(race.time, config.offsetFinale)
        pnum = teams.count()
        rname = ''
        if teams.count() == 0:
            races = 0
        elif teams.count() == 1:
            races = 1
        else:
            if config.raceToTopFinal:
                # if race-to-top race mode is active, leave lane free for victor from previous race, except in the first race
                races = math.ceil((teams.count() - 1) / max(1, (config.lanesPerRace - 1)))
            else:
                # fully populate all races
                races = math.ceil(teams.count() / max(1, config.lanesPerRace))
        for rnum in range(races):
            race = Race()
            race.time = start
            race.name = '{}{}'.format(config.finalPrefix, rnum + 1)
            race.save()

            # create finale draw assignments
            if rnum == 0:
                # lane count for first race might not match number of available lanes
                if config.raceToTopFinal:
                    # if race-to-top race mode is active, leave lane free for victor from previous race
                    lanes = teams.count() - (races - 1) * (config.lanesPerRace - 1)
                else:
                    # populate all races
                    lanes = teams.count() - (races - 1) * config.lanesPerRace
            else:
                lanes = config.lanesPerRace                                         # last race is always full if possible
            for lnum in range(lanes):
                rdm = RaceDrawMode()
                rdm.race_id = race.id
                rdm.lane = lnum + 1                                                 # start lane number at 1
                if rnum == 0 or lnum != 0 or not config.raceToTopFinal:
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
    for hnum in range(config.heatCount):
        if hnum > 0:
            start = combineTimeOffset(start, config.intermissionHeat)
        start = updateRaces('{pre}{num}'.format(pre=config.heatPrefix, num=(hnum + 1)), start, config.intervalHeat)

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
                'count': teams_active,
                'tooltip': '{title} {status}: {count}'.format(title=config.teamTableHeaderTeams, status=config.activeTeams, count=teams_active)
            }
        )
    teams_wait = Team.objects.filter(active=True, wait=True).count()
    if teams_active:
        menu_teams['notifications'].append(
            {
                'level': 'warning',
                'count': teams_wait,
                'tooltip': '{title} {status}: {count}'.format(title=config.teamTableHeaderTeams, status=config.waitlistTeams, count=teams_wait)
            }
        )
    teams_inactive = Team.objects.filter(active=False).count()
    if teams_active:
        menu_teams['notifications'].append(
            {
                'level': 'secondary',
                'count': teams_inactive,
                'tooltip': '{title} {status}: {count}'.format(title=config.teamTableHeaderTeams, status=config.inactiveTeams, count=teams_inactive)
            }
        )

    menu_trainings = {
        'id': 'trainings',
        'title': config.trainingsTitle,
        'url': 'trainings',
        'thumb': config.trainingsIcon,
        'active': True if id == 'trainings' else False,
        'notifications': []
    }
    trainings_upcoming = len(getTrainingsList(upcomingOnly=True))
    if trainings_upcoming:
        menu_trainings['notifications'].append(
            {
                'level': 'warning',
                'count': trainings_upcoming,
                'tooltip': '{title}: {count}'.format(title=config.trainingsTitleUpcoming, count=trainings_upcoming)
            }
        )
    trainings_past = len(getTrainingsList(pastOnly=True))
    if trainings_past:
        menu_trainings['notifications'].append(
            {
                'level': 'success',
                'count': trainings_past,
                'tooltip': '{title}: {count}'.format(title=config.trainingsTitlePast, count=trainings_past)
            }
        )
    trainings_inactive = len(getTrainingsList(active=False))
    if trainings_inactive:
        menu_trainings['notifications'].append(
            {
                'level': 'secondary',
                'count': trainings_inactive,
                'tooltip': '{title}: {count}'.format(title=config.trainingsTitleInactive, count=trainings_inactive)
            }
        )

    menu_billing = {
        'id': 'billing',
        'title': config.billingTitle,
        'url': 'billing',
        'thumb': config.billingIcon,
        'active': True if id == 'billing' else False,
        'notifications': []
    }

    menu_calendar = {
        'id': 'calendar',
        'title': config.calendarTitle,
        'url': 'calendar',
        'thumb': config.calendarIcon,
        'active': True if id == 'calendar' else False,
        'notifications': []
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
                'count': skippers_active,
                'tooltip': '{title} {status}: {count}'.format(title=config.skippersTitle, status=config.activeSkipperTitle, count=skippers_active)
            }
        )
    skippers_inactive = Skipper.objects.filter(active=False).count()
    if skippers_inactive:
        menu_skippers['notifications'].append(
            {
                'level': 'secondary',
                'count': skippers_inactive,
                'tooltip': '{title} {status}: {count}'.format(title=config.skippersTitle, status=config.inactiveSkipperTitle, count=skippers_inactive)
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
                'count': started,
                'tooltip': '{title}: {status}'.format(title=config.raceCurrentTitle, status=started)
            }
        )
    elif last is not None:
        menu_times['notifications'].append(
            {
                'level': 'success',
                'count': last,
                'tooltip': '{title}: {status}'.format(title=config.raceLastTitle, status=last)
            }
        )
    if next is not None:
        menu_times['notifications'].append(
            {
                'level': 'danger',
                'count': next,
                'tooltip': '{title}: {status}'.format(title=config.raceNextTitle, status=next)
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
                'count': current_race_block,
                'tooltip': '{title}: {status}'.format(title=config.currentRaceBlockTitle, status=current_race_block)
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
        siteData['menu'].append(menu_billing)

    siteData['menu'].append(menu_timetable)

    if config.activateCalendar or user.is_authenticated:
        siteData['menu'].append(menu_calendar)

    if user and user.is_authenticated and user.is_staff:
        siteData['menu'].append(menu_times)

    if config.activateResults or user.is_authenticated:
        siteData['menu'].append(menu_results)

    if user and user.is_authenticated:
        siteData['menu'].append(menu_display)

    siteData['menu'].append(menu_toggle)

    if user and user.is_authenticated and user.is_staff:
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
        attendees = RaceAssign.objects.filter(race_id=race.id, time__gt=0.0).order_by('time')
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
                attendee = RaceAssign.objects.filter(race_id=race.id, lane=(lnum + 1))[0]       # For now take only the first returned
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
                    if not last_race and config.raceToTopFinal and lane['place'] == 1:
                        continue
                    lane['rank'] = rank_finale - (lanesInRace - lane['place'])
                rank_finale -= lanesInRace if last_race or not config.raceToTopFinal else lanesInRace - 1

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
                # only skip rank assignment if race-to-top race mode is active
                if not last_race and config.raceToTopFinal and lane['place'] == 1:
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
            rank_finale -= lanesInRace if last_race or not config.raceToTopFinal else lanesInRace - 1

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
    return all(finished) and len(finished) > 0

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

def getTimesData():
    data = {
        'current_race': {},
        'skippers': [''],
        'skipper_icon': 'person',
        'time_icon': 'clock-history'
    }

    current_race = None

    for race in Race.objects.all():
        if current_race is None:
            attendees = RaceAssign.objects.filter(race_id=race.id)
            if sum([1 if attendee.time else 0 for attendee in attendees]) < len(attendees):
                current_race = race.name
        else:
            break

    data['current_race'] = current_race

    skippers = Skipper.objects.all()
    for skipper in skippers:
        data['skippers'].append(
            {
                'name': skipper.name,
                'active': skipper.active
            }
        )

    return data

def getMainSettings():
    settings = [
        {
            'title': config.settingsHeaderRegatta,
            'controls': [
                {
                    'id': 'eventTitle',
                    'name': config.siteNameDesc,
                    'type': 'text',
                    'value': config.siteName,
                    'icon': 'signpost',
                    'classes': 'col-12 col-xxl-6 col-lg-9'
                },
                {
                    'id': 'eventAbbreviation',
                    'name': config.siteAbbrDesc,
                    'type': 'text',
                    'value': config.siteAbbr,
                    'icon': 'tag',
                    'classes': 'col-12 col-xxl-2 col-lg-3'
                },
                {
                    'id': 'eventDate',
                    'name': config.eventDateDesc,
                    'type': 'date',
                    'value': config.eventDate,
                    'icon': 'calendar3-event',
                    'classes': 'col-12 col-xxl-2 col-xl-3 col-md-6'
                },
                {
                    'id': 'registrationDate',
                    'name': config.registrationDateDesc,
                    'type': 'date',
                    'value': config.registrationDate,
                    'icon': 'calendar3-event',
                    'classes': 'col-12 col-xxl-2 col-xl-3 col-md-6'
                }
            ]
        },
        {
            'title': config.settingsHeaderAccess,
            'controls': [
                {
                    'id': 'activateResults',
                    'name': config.activateResultsDesc,
                    'type': 'checkbox',
                    'value': config.activateResults,
                    'icon': 'check-square',
                    'classes': 'col-auto',
                    'active': config.activeResultsDesc,
                    'inactive': config.inactiveResultsDesc
                },
                {
                    'id': 'anonymousMonitor',
                    'name': config.anonymousMonitorDesc,
                    'type': 'checkbox',
                    'value': config.anonymousMonitor,
                    'icon': 'check-square',
                    'classes': 'col-auto',
                    'active': config.activeResultsDesc,
                    'inactive': config.inactiveResultsDesc
                },
                {
                    'id': 'activateCalendar',
                    'name': config.activateCalendarDesc,
                    'type': 'checkbox',
                    'value': config.activateCalendar,
                    'icon': 'calendar-check',
                    'classes': 'col-auto',
                    'active': config.activeResultsDesc,
                    'inactive': config.inactiveResultsDesc
                }
            ]
        },
        {
            'title': config.settingsTimetable,
            'controls': [
                {
                    'id': 'timeBegin',
                    'name': config.timeBeginDesc,
                    'type': 'time',
                    'value': config.timeBegin,
                    'icon': 'clock',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'offsetHeat',
                    'name': config.offsetHeatDesc,
                    'type': 'number',
                    'value': config.offsetHeat.seconds // 60,
                    'icon': 'clock-history',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'intermissionHeat',
                    'name': config.intermissionHeatDesc,
                    'type': 'number',
                    'value': config.intermissionHeat.seconds // 60,
                    'icon': 'clock-history',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'offsetFinale',
                    'name': config.offsetFinaleDesc,
                    'type': 'number',
                    'value': config.offsetFinale.seconds // 60,
                    'icon': 'clock-history',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'offsetCeremony',
                    'name': config.offsetCeremonyDesc,
                    'type': 'number',
                    'value': config.offsetCeremony.seconds // 60,
                    'icon': 'clock-history',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'lanesPerRace',
                    'name': config.lanesPerRaceDesc,
                    'type': 'number',
                    'value': config.lanesPerRace,
                    'min': config.lanesPerRaceMin,
                    'max': config.lanesPerRaceMax,
                    'icon': 'layout-three-columns',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'heatCount',
                    'name': config.heatCountDesc,
                    'type': 'number',
                    'value': config.heatCount,
                    'min': config.heatCountMin,
                    'max': config.heatCountMax,
                    'icon': 'repeat',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'intervalHeat',
                    'name': config.intervalHeatDesc,
                    'type': 'number',
                    'value': config.intervalHeat.seconds // 60,
                    'icon': 'distribute-horizontal',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'intervalFinal',
                    'name': config.intervalFinalDesc,
                    'type': 'number',
                    'value': config.intervalFinal.seconds // 60,
                    'icon': 'distribute-horizontal',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'boardingTime',
                    'name': config.boardingTimeDesc,
                    'type': 'number',
                    'value': config.boardingTime.seconds // 60,
                    'icon': 'clock-history',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'raceToTopFinal',
                    'name': config.raceToTopFinalDesc,
                    'type': 'checkbox',
                    'value': config.raceToTopFinal,
                    'icon': 'calendar-check',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2',
                    'active': config.active,
                    'inactive': config.inactive
                },
                {
                    'id': 'refreshTimes',
                    'name': config.refreshTimetableText,
                    'type': 'button',
                    'icon': config.refreshTimetableIcon,
                    'classes': 'col-auto'
                }
            ]
        },
        {
            'title': config.settingsTrainings,
            'controls': [
                {
                    'id': 'intervalTrainingBegin',
                    'name': config.intervalTrainingBeginLabel,
                    'type': 'number',
                    'value': config.intervalTrainingBegin.seconds // 60,
                    'icon': 'clock-history',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'firstTrainingTime',
                    'name': config.firstTrainingTimeLabel,
                    'type': 'time',
                    'value': config.firstTrainingTime,
                    'icon': 'clock',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'lastTrainingTime',
                    'name': config.lastTrainingTimeLabel,
                    'type': 'time',
                    'value': config.lastTrainingTime,
                    'icon': 'clock',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'lengthTraining',
                    'name': config.intervalTrainingLengthLabel,
                    'type': 'number',
                    'value': config.intervalTrainingLength.seconds // 60,
                    'icon': 'clock-history',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                }
            ]
        },
        {
            'title': config.billingTitle,
            'controls': [
                {
                    'id': 'eventFee',
                    'name': config.eventFeeLabel,
                    'type': 'number',
                    'value': config.eventFee,
                    'icon': 'currency-euro',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'trainingsFee',
                    'name': config.trainingsFeeLabel,
                    'type': 'number',
                    'value': config.trainingsFee,
                    'icon': 'currency-euro',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'skipperTrainingsCompensation',
                    'name': config.skipperTrainingsCompLabel,
                    'type': 'number',
                    'value': config.skipperTrainingsCompensation,
                    'icon': 'currency-euro',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'firstTrainingIsFree',
                    'name': config.firstTrainingIsFreeLabel,
                    'type': 'checkbox',
                    'value': config.firstTrainingIsFree,
                    'icon': 'check-square',
                    'classes': 'col-auto',
                    'active': config.firstTrainingIsFreeActive,
                    'inactive': config.firstTrainingIsFreeInactive
                }
            ]
        },
        {
            'title': config.settingsHeaderMonitor,
            'controls': [
                {
                    'id': 'displayOverscan',
                    'name': config.overscanDesc,
                    'type': 'number',
                    'value': config.overscan,
                    'icon': 'aspect-ratio',
                    'min': 0,
                    'max': config.overscanMax,
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'durationMonitorSlide',
                    'name': config.displayIntervalDesc,
                    'type': 'number',
                    'value': int(config.displayInterval / 1e3),
                    'icon': 'clock-history',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'displayDataRefresh',
                    'name': config.displayDataRefreshDesc,
                    'type': 'number',
                    'value': int(config.displayDataRefresh / 1e3),
                    'icon': 'clock-history',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'maxRacesPerPage',
                    'name': config.maxRacesPerPageDesc,
                    'type': 'number',
                    'value': config.maxRacesPerPage,
                    'icon': 'file-ruled',
                    'classes': 'col-12 col-sm-6 col-md-4 col-lg-3 col-xxl-2'
                },
                {
                    'id': 'liveResultsHint',
                    'name': config.liveResultsHintDesc,
                    'type': 'text',
                    'value': config.liveResultsHint,
                    'icon': 'info-square',
                    'classes': 'col-12 col-lg-6'
                },
                {
                    'id': 'siteDomain',
                    'name': config.liveResultsDomainDesc,
                    'type': 'text',
                    'value': config.domain,
                    'icon': 'link',
                    'classes': 'col-12 col-lg-6'
                }
            ]
        },
        {
            'title': config.settingsHeaderFooter,
            'controls': [
                {
                    'id': 'ownerName',
                    'name': config.ownerNameDesc,
                    'type': 'text',
                    'value': config.ownerName,
                    'icon': 'person-circle',
                    'classes': 'col-12 col-lg-6'
                },
                {
                    'id': 'sponsorName',
                    'name': config.sponsorNameDesc,
                    'type': 'text',
                    'value': config.sponsorName,
                    'icon': 'building',
                    'classes': 'col-12 col-lg-6'
                },
                {
                    'id': 'ownerUrl',
                    'name': config.ownerUrlDesc,
                    'type': 'url',
                    'value': config.ownerUrl,
                    'icon': 'link-45deg',
                    'classes': 'col-12 col-lg-6'
                },
                {
                    'id': 'sponsorUrl',
                    'name': config.sponsorUrlDesc,
                    'type': 'url',
                    'value': config.sponsorUrl,
                    'icon': 'link-45deg',
                    'classes': 'col-12 col-lg-6'
                },
                {
                    'id': 'ownerLogo',
                    'name': config.ownerLogoDesc,
                    'type': 'image',
                    'value': config.ownerLogo,
                    'icon': 'image',
                    'options': getLogoSelection(),
                    'classes': 'col-12 col-md-6 col-lg-3',
                    'bg_class': 'bg-dark'
                },
                {
                    'id': 'sponsorLogo',
                    'name': config.sponsorLogoDesc,
                    'type': 'image',
                    'value': config.sponsorLogo,
                    'icon': 'image',
                    'options': getLogoSelection(),
                    'classes': 'col-12 col-md-6 col-lg-3',
                    'bg_class': 'bg-dark'
                },
                {
                    'id': 'ownerLogoReport',
                    'name': config.ownerLogoReportDesc,
                    'type': 'image',
                    'value': config.ownerLogoReport,
                    'icon': 'image',
                    'options': getLogoSelection(),
                    'classes': 'col-12 col-md-6 col-lg-3',
                    'bg_class': 'bg-light'
                },
                {
                    'id': 'sponsorLogoReport',
                    'name': config.sponsorLogoReportDesc,
                    'type': 'image',
                    'value': config.sponsorLogoReport,
                    'icon': 'image',
                    'options': getLogoSelection(),
                    'classes': 'col-12 col-md-6 col-lg-3',
                    'bg_class': 'bg-light'
                },
                {
                    'id': 'ownerName2',
                    'name': config.ownerName2Desc,
                    'type': 'text',
                    'value': config.ownerName2,
                    'icon': 'person-circle',
                    'classes': 'col-12 col-lg-6'
                },
                {
                    'id': 'sponsorName2',
                    'name': config.sponsorName2Desc,
                    'type': 'text',
                    'value': config.sponsorName2,
                    'icon': 'building',
                    'classes': 'col-12 col-lg-6'
                },
                {
                    'id': 'ownerUrl2',
                    'name': config.ownerUrl2Desc,
                    'type': 'url',
                    'value': config.ownerUrl2,
                    'icon': 'link-45deg',
                    'classes': 'col-12 col-lg-6'
                },
                {
                    'id': 'sponsorUrl2',
                    'name': config.sponsorUrl2Desc,
                    'type': 'url',
                    'value': config.sponsorUrl2,
                    'icon': 'link-45deg',
                    'classes': 'col-12 col-lg-6'
                },
                {
                    'id': 'ownerLogo2',
                    'name': config.ownerLogo2Desc,
                    'type': 'image',
                    'value': config.ownerLogo2,
                    'icon': 'image',
                    'options': getLogoSelection(),
                    'classes': 'col-12 col-md-6 col-lg-3',
                    'bg_class': 'bg-dark'
                },
                {
                    'id': 'sponsorLogo2',
                    'name': config.sponsorLogo2Desc,
                    'type': 'image',
                    'value': config.sponsorLogo2,
                    'icon': 'image',
                    'options': getLogoSelection(),
                    'classes': 'col-12 col-md-6 col-lg-3',
                    'bg_class': 'bg-dark'
                },
                {
                    'id': 'ownerLogo2Report',
                    'name': config.ownerLogo2ReportDesc,
                    'type': 'image',
                    'value': config.ownerLogo2Report,
                    'icon': 'image',
                    'options': getLogoSelection(),
                    'classes': 'col-12 col-md-6 col-lg-3',
                    'bg_class': 'bg-light'
                },
                {
                    'id': 'sponsorLogo2Report',
                    'name': config.sponsorLogo2ReportDesc,
                    'type': 'image',
                    'value': config.sponsorLogo2Report,
                    'icon': 'image',
                    'options': getLogoSelection(),
                    'classes': 'col-12 col-md-6 col-lg-3',
                    'bg_class': 'bg-light'
                }
            ]
        }
    ]

    return settings

# Get content for the advanced settings section
def getAdvancedSettings():
    settings = [
        {
            'title': config.devOptionsTimetable,
            'folded': True,
            'buttons': [
                {
                    'id': 'resetFinals',
                    'value': 'ResetFinals',
                    'icon': config.resetFinalsIcon,
                    'icon_alt': 'reset_finals',
                    'text': config.resetFinals,
                    'classes': 'btn-warning btn_icon btn_lg',
                    'modal': {
                        'id': 'resetFinalsModal',
                        'classes': 'text-dark',
                        'header': {
                            'id': 'resetFinalsLabel',
                            'title': config.resetFinals,
                            'classes': 'bg-warning text-dark'
                        },
                        'body': {
                            'icon': config.questionIcon,
                            'text': config.warningResetFinals
                        },
                        'footer': {
                            'buttons': [
                                {
                                    'id': 'resetFinalsSubmit',
                                    'value': 'ResetFinals',
                                    'classes': 'btn-warning btn_icon',
                                    'action': "update_setting('resetFinals')",
                                    'icon': config.resetFinalsIcon,
                                    'icon_alt': 'reset_finals',
                                    'icon_class': '',
                                    'text': config.resetFinals
                                },
                                {
                                    'id': 'resetFinalsCancel',
                                    'value': 'resetFinalsCancel',
                                    'classes': 'btn-secondary btn_icon',
                                    'icon': config.cancelTeamIcon,
                                    'icon_alt': 'cancelResetFinals',
                                    'icon_class': 'p-0',
                                    'text': config.submitAbort
                                }
                            ],
                            'spinner': {
                                'id': 'wait_resetFinals',
                                'classes': 'text-primary'
                            }
                        }
                    },
                },
                {
                    'id': 'resetHeats',
                    'value': 'ResetHeats',
                    'icon': config.resetHeatsIcon,
                    'icon_alt': 'reset_heats',
                    'text': config.resetHeats,
                    'classes': 'btn-warning btn_icon btn_lg',
                    'modal': {
                        'id': 'resetHeatsModal',
                        'classes': 'text-dark',
                        'header': {
                            'id': 'resetHeatsLabel',
                            'title': config.resetHeats,
                            'classes': 'bg-warning text-dark'
                        },
                        'body': {
                            'icon': config.questionIcon,
                            'text': config.warningResetHeats
                        },
                        'footer': {
                            'buttons': [
                                {
                                    'id': 'resetHeatsSubmit',
                                    'value': 'ResetHeats',
                                    'classes': 'btn-warning btn_icon',
                                    'action': "update_setting('resetHeats')",
                                    'icon': config.resetHeatsIcon,
                                    'icon_alt': 'reset_heats',
                                    'icon_class': '',
                                    'text': config.resetHeats
                                },
                                {
                                    'id': 'resetHeatsCancel',
                                    'value': 'resetHeatsCancel',
                                    'classes': 'btn-secondary btn_icon',
                                    'icon': config.cancelTeamIcon,
                                    'icon_alt': 'cancelResetHeats',
                                    'icon_class': 'p-0',
                                    'text': config.submitAbort
                                }
                            ],
                            'spinner': {
                                'id': 'wait_resetHeats',
                                'classes': 'text-primary'
                            }
                        }
                    },
                },
                {
                    'id': 'resetTimetable',
                    'value': 'ResetTimetable',
                    'icon': config.resetTimetableIcon,
                    'icon_alt': 'reset_timetable',
                    'text': config.resetTimetable,
                    'classes': 'btn-danger btn_icon btn_lg',
                    'modal': {
                        'id': 'resetTimetableModal',
                        'classes': 'text-dark',
                        'header': {
                            'id': 'resetTimetableLabel',
                            'title': config.resetTimetable,
                            'classes': 'bg-danger text-light'
                        },
                        'body': {
                            'icon': config.questionIcon,
                            'text': config.warningResetTimetable
                        },
                        'footer': {
                            'buttons': [
                                {
                                    'id': 'resetTimetableSubmit',
                                    'value': 'ResetTimetable',
                                    'classes': 'btn-danger btn_icon',
                                    'action': "update_setting('resetTimetable')",
                                    'icon': config.resetTimetableIcon,
                                    'icon_alt': 'reset_timetable',
                                    'icon_class': '',
                                    'text': config.resetTimetable
                                },
                                {
                                    'id': 'resetTimetableCancel',
                                    'value': 'resetTimetableCancel',
                                    'classes': 'btn-secondary btn_icon',
                                    'icon': config.cancelTeamIcon,
                                    'icon_alt': 'cancelResetTimetable',
                                    'icon_class': 'p-0',
                                    'text': config.submitAbort
                                }
                            ],
                            'spinner': {
                                'id': 'wait_resetTimetable',
                                'classes': 'text-primary'
                            }
                        }
                    },
                }
            ]
        },
        {
            'title': config.devOptionsData,
            'folded': True,
            'buttons': [
                {
                    'id': 'resetSkippers',
                    'value': 'ResetSkippers',
                    'icon': config.resetSkippersIcon,
                    'icon_alt': 'reset_skippers',
                    'text': config.resetSkippers,
                    'classes': 'btn-primary btn_icon btn_lg',
                    'modal': {
                        'id': 'resetSkippersModal',
                        'classes': 'text-dark',
                        'header': {
                            'id': 'resetSkippersLabel',
                            'title': config.resetSkippers,
                            'classes': 'bg-warning text-dark'
                        },
                        'body': {
                            'icon': config.questionIcon,
                            'text': config.warningResetSkippers
                        },
                        'footer': {
                            'buttons': [
                                {
                                    'id': 'resetSkippersSubmit',
                                    'value': 'ResetSkippers',
                                    'classes': 'btn-primary btn_icon',
                                    'action': "update_setting('resetSkippers')",
                                    'icon': config.resetSkippersIcon,
                                    'icon_alt': 'reset_skippers',
                                    'icon_class': '',
                                    'text': config.resetSkippers
                                },
                                {
                                    'id': 'resetSkippersCancel',
                                    'value': 'resetSkippersCancel',
                                    'classes': 'btn-secondary btn_icon',
                                    'icon': config.cancelTeamIcon,
                                    'icon_alt': 'cancelResetSkippers',
                                    'icon_class': 'p-0',
                                    'text': config.submitAbort
                                }
                            ],
                            'spinner': {
                                'id': 'wait_resetSkippers',
                                'classes': 'text-primary'
                            }
                        }
                    },
                },
                {
                    'id': 'resetTraining',
                    'value': 'ResetTraining',
                    'icon': config.resetTrainingIcon,
                    'icon_alt': 'reset_training',
                    'text': config.resetTraining,
                    'classes': 'btn-primary btn_icon btn_lg',
                    'modal': {
                        'id': 'resetTrainingModal',
                        'classes': 'text-dark',
                        'header': {
                            'id': 'resetTrainingLabel',
                            'title': config.resetTraining,
                            'classes': 'bg-warning text-dark'
                        },
                        'body': {
                            'icon': config.questionIcon,
                            'text': config.warningResetTraining
                        },
                        'footer': {
                            'buttons': [
                                {
                                    'id': 'resetTrainingSubmit',
                                    'value': 'ResetTraining',
                                    'classes': 'btn-primary btn_icon',
                                    'action': "update_setting('resetTraining')",
                                    'icon': config.resetTrainingIcon,
                                    'icon_alt': 'reset_training',
                                    'icon_class': '',
                                    'text': config.resetTraining
                                },
                                {
                                    'id': 'resetTrainingCancel',
                                    'value': 'resetTrainingCancel',
                                    'classes': 'btn-secondary btn_icon',
                                    'icon': config.cancelTeamIcon,
                                    'icon_alt': 'cancelResetTraining',
                                    'icon_class': 'p-0',
                                    'text': config.submitAbort
                                }
                            ],
                            'spinner': {
                                'id': 'wait_resetTraining',
                                'classes': 'text-primary'
                            }
                        }
                    },
                },
                {
                    'id': 'resetTeams',
                    'value': 'ResetTeams',
                    'icon': config.resetTeamsIcon,
                    'icon_alt': 'reset_teams',
                    'text': config.resetTeams,
                    'classes': 'btn-danger btn_icon btn_lg',
                    'modal': {
                        'id': 'resetTeamsModal',
                        'classes': 'text-dark',
                        'header': {
                            'id': 'resetTeamsLabel',
                            'title': config.resetTeams,
                            'classes': 'bg-danger text-light'
                        },
                        'body': {
                            'icon': config.questionIcon,
                            'text': config.warningResetTeams
                        },
                        'footer': {
                            'buttons': [
                                {
                                    'id': 'resetTeamsSubmit',
                                    'value': 'ResetTeams',
                                    'classes': 'btn-danger btn_icon',
                                    'action': "update_setting('resetTeams')",
                                    'icon': config.resetTeamsIcon,
                                    'icon_alt': 'reset_teams',
                                    'icon_class': '',
                                    'text': config.resetTeams
                                },
                                {
                                    'id': 'resetTeamsCancel',
                                    'value': 'resetTeamsCancel',
                                    'classes': 'btn-secondary btn_icon',
                                    'icon': config.cancelTeamIcon,
                                    'icon_alt': 'cancelResetTeams',
                                    'icon_class': 'p-0',
                                    'text': config.submitAbort
                                }
                            ],
                            'spinner': {
                                'id': 'wait_resetTeams',
                                'classes': 'text-primary'
                            }
                        }
                    },
                },
                {
                    'id': 'resetTeamSignups',
                    'value': 'ResetTeamSignups',
                    'icon': config.resetTeamSignupsIcon,
                    'icon_alt': 'reset_team_signups',
                    'text': config.resetTeamSignups,
                    'classes': 'btn-primary btn_icon btn_lg',
                    'modal': {
                        'id': 'resetTeamSignupsModal',
                        'classes': 'text-dark',
                        'header': {
                            'id': 'resetTeamSignupsLabel',
                            'title': config.resetTeamSignups,
                            'classes': 'bg-primary text-light'
                        },
                        'body': {
                            'icon': config.questionIcon,
                            'text': config.warningResetTeamSignups
                        },
                        'footer': {
                            'buttons': [
                                {
                                    'id': 'resetTeamSignupsSubmit',
                                    'value': 'ResetTeamSignups',
                                    'classes': 'btn-primary btn_icon',
                                    'action': "update_setting('resetTeamSignups')",
                                    'icon': config.resetTeamSignupsIcon,
                                    'icon_alt': 'reset_team_signups',
                                    'icon_class': '',
                                    'text': config.resetTeamSignups
                                },
                                {
                                    'id': 'resetTeamSignupsCancel',
                                    'value': 'resetTeamSignupsCancel',
                                    'classes': 'btn-secondary btn_icon',
                                    'icon': config.cancelTeamIcon,
                                    'icon_alt': 'cancelResetTeamSignups',
                                    'icon_class': 'p-0',
                                    'text': config.submitAbort
                                }
                            ],
                            'spinner': {
                                'id': 'wait_resetTeamSignups',
                                'classes': 'text-primary'
                            }
                        }
                    },
                }
            ]
        }
    ]

    return settings

# check if all heats are finished and if so, create rankings and fill finals
# TODO: Does not change race count for finals. This means switching race mode does
# result in an invalid finale timetable (teams/races missing from finale).
def populateFinals(race_assignment: RaceAssign = None):
    if getCurrentRaceBlock() == config.finalPrefix:
        # get all final races and sort after race names in reverse order, but obey number ordering
        races = Race.objects.filter(name__startswith = config.finalPrefix)
        races_sorted = [(race.id, race.name) for race in races]
        races_sorted.sort(key=lambda x:[int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x[1])], reverse=True)
        race_ids = [race[0] for race in races_sorted]

        # for already running finals, decide if a winner from a particular final race can ascend one race
        if race_assignment and config.raceToTopFinal:
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

                        # leave lane free for winner from previous race if race-to-top race mode is active
                        if config.raceToTopFinal and (race_id != race_ids[-1] and lane == 0 or lane + 1 > len(rankings) - rank_id):
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

# Remove all heats including racing times from the DB including finals and race assignments
def clearRaces():
    # delete all race assignments for the heats
    RaceAssign.objects.all().delete()

    # delete all race draw modes
    RaceDrawMode.objects.all().delete()

    # remove all races
    Race.objects.all().delete()

# Remove all heat racing times from the DB and clear all finals
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

# Gather data for the impressum
def getImpressumData():
    impressum = None
    try:
        with open(os.path.join(dj_settings.STATIC_ROOT, 'data', 'impressum.json'), encoding='utf-8') as impressum_json:
            impressum = json.load(impressum_json)
    except:
        pass
    return impressum

# Make a copy of the database
# TODO: This needs to be reworked, just filecopy is a bad hack!
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

# Get last backup timestamp
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

# Removce all skippers from the database
def clearSkippers():
    # Clear all skippers from race assignments
    assignments = RaceAssign.objects.all()
    for assignment in assignments:
        assignment.skipper_id = None
        assignment.save()

    # Empty Skipper DB
    Skipper.objects.all().delete()

# Remove all teams from the database
def clearTeams():
    # Clear all heats and finals including race assignments
    clearRaces()

    # Empty Team DB
    Team.objects.all().delete()

# Remove all trainings from the database
def clearTrainings():
    # Empty Training DB
    Training.objects.all().delete()

# reset all signup data for the teams and make all teams inactive
def resetTeamSignups():
    for team in Team.objects.all():
        team.active = False
        team.wait = False
        team.position = None
        team.date = None
        team.save()

def getLogoSelection():
    logo_list = ['']    # add empty selection
    for f in glob(os.path.join(dj_settings.MEDIA_ROOT, 'images/*.png')):
        logo_list.append(os.path.basename(f))

    return logo_list