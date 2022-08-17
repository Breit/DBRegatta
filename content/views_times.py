from constance import config
from django.shortcuts import render, redirect

from .views_main import getSiteData
from .views_timetable import combineTimeOffset, getFirstRaceTime, getRaces
from .models import Race, RaceAssign, Team, RaceDrawMode

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

def times(request):
    siteData = getSiteData('times')
    siteData['times'] = getTimeTableContent()

    if request.method == "POST":
        # TODO
        pass

    return render(request, 'times.html', siteData)