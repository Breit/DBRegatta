from constance import config
from django.shortcuts import render

from .views_times import getRaceTimes
from .views_timetable import combineTimeOffset
from .views_main import getSiteData
from .models import Race, RaceAssign, Team

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

def display(request):
    siteData = getSiteData('display')
    siteData['display'] = {
        'timetable': getCurrentTimeTable(),
        'rankings': getRankingTable()
    }
    return render(request, 'display.html', siteData)
