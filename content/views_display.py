from constance import config
from django.shortcuts import render

from .views_times import getRaceTimes
from .views_timetable import combineTimeOffset
from .views_main import getSiteData


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
    rankings = []
    # TODO
    return rankings

def display(request):
    siteData = getSiteData('display')
    siteData['display'] = {
        'timetable': getCurrentTimeTable(),
        'rankings': getRankings()
    }
    return render(request, 'display.html', siteData)
