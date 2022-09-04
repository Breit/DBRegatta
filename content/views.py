from django.shortcuts import render, redirect

from .views_helper import *

def main(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated:
        return redirect('/timetable')
    else:
        return redirect('/times')

def teams(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated:
        return redirect('/')

    siteData = getSiteData('teams', request.user)
    siteData['content'] = getTeamContent()

    if request.method == "POST":
        # activate the add-new-team form
        if 'show_add_form' in request.POST:
            siteData['content']['forms']['add'] = True

        # submit a new team
        elif 'add_team' in request.POST:
            newTeamForm = TeamForm(request.POST)
            if Team.objects.filter(name=request.POST['name']).exists():
                siteData['content']['forms']['add'] = True
                siteData['content']['forms']['form'] = newTeamForm
            if newTeamForm['date'].data == '':
                siteData['content']['forms']['add'] = True
                siteData['content']['forms']['form'] = newTeamForm
                newTeamForm.add_error('date', 'Date missing')
            elif newTeamForm.is_valid():
                newTeamForm.save()
                siteData['content'] = getTeamContent()              # refresh from DB
                return redirect('/teams')

        # abort submitting teams changes
        elif 'cancel_team' in request.POST:
            return redirect('/teams')

        # toggle team activation
        elif 'activate_team' in request.POST:
            if Team.objects.filter(name=request.POST['activate_team']).exists():
                modTeam = Team.objects.get(name=request.POST['activate_team'])
                modTeam.active = not modTeam.active
                modTeam.save()
                siteData['content'] = getTeamContent()              # refresh from DB
            return redirect('/teams')

        # toggle team waitlist
        elif 'waitlist_team' in request.POST:
            if Team.objects.filter(name=request.POST['waitlist_team']).exists():
                modTeam = Team.objects.get(name=request.POST['waitlist_team'])
                modTeam.wait = not modTeam.wait
                if modTeam.wait:
                    modTeam.active = True
                modTeam.save()
                siteData['content'] = getTeamContent()              # refresh from DB
            return redirect('/teams')

        # delete team from database
        elif 'delete_team' in request.POST:
            if Team.objects.filter(name = request.POST['delete_team']).exists():
                modTeam = Team.objects.get(name = request.POST['delete_team'])
                modTeam.delete()
                siteData['content'] = getTeamContent()              # refresh from DB
            return redirect('/teams')

        # show edit team form
        elif 'edit_team' in request.POST:
            if Team.objects.filter(id = request.POST['edit_team']).exists():
                return redirect('/teams?edit_id={}'.format(request.POST['edit_team']))

        # submit_mod_team
        elif 'mod_team' in request.POST:
            if 'edit_id' in request.GET:
                if Team.objects.filter(id=request.GET['edit_id']).exists():
                    modTeamForm = TeamForm(
                        request.POST,
                        instance = Team.objects.get(id = request.GET['edit_id'])
                    )
                    if modTeamForm.is_valid():
                        modTeamForm.save()
                        siteData['content'] = getTeamContent()      # refresh from DB
                        return redirect('/teams')
                    else:
                        siteData['content']['forms']['mod'] = True
                        siteData['content']['forms']['form'] = modTeamForm
                        siteData['content']['forms']['id'] = int(request.GET['edit_id'])
    else:  # handle request.GET
        # prepare form for modifying a team
        if 'edit_id' in request.GET:
            if Team.objects.filter(id = request.GET['edit_id']).exists():
                siteData['content']['forms']['id'] = int(request.GET['edit_id'])
                siteData['content']['forms']['mod'] = True
                siteData['content']['forms']['form'] = TeamForm(
                    instance = Team.objects.get(id = request.GET['edit_id'])
                )

    return render(request, 'teams.html', siteData)

def trainings(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated:
        return redirect('/')

    siteData = getSiteData('trainings', request.user)
    siteData['content'] = {}
    return render(request, 'trainings.html', siteData)

def timetable(request):
    # handle login/logout
    loginUser(request)

    siteData = getSiteData('timetable', request.user)
    siteData['timetable'] = getTimeTableContent()

    if request.user.is_authenticated:
        siteData['controls'] = getTimeTableSettings()

        if request.method == "POST":
            if 'content' in request.POST and 'enable' in request.POST:
                try:
                    post = Post.objects.get(site='timetable')
                except Post.DoesNotExist:
                    post = Post()
                    post.site = 'timetable'
                post.enable = request.POST['enable'] == 'on'
                post.content = request.POST['content']
                post.save()
            elif 'timeBegin' in request.POST:
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
            elif 'createTimetable' in request.POST:
                createTimeTable()
            elif 'refreshTimes' in request.POST:
                updateTimeTable()
            return redirect('/timetable')
    else:
        try:
            post = Post.objects.get(site='timetable')
            if post.enable:
                siteData['post'] = post.content
        except:
            pass

    return render(request, 'timetable.html', siteData)

def times(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated:
        return redirect('/')

    # shortcut to URL with specific race_id
    if request.method == "POST" and 'race_select' in request.POST:
        race = None
        if request.POST['race_select']:
            try:
                race = Race.objects.get(name = request.POST['race_select'])
            except:
                pass
        else:
            return redirect('/times')
        if race:
            return redirect('/times?race_id={}'.format(race.id))

    # construct site data
    siteData = getSiteData('times', request.user)
    if 'race_id' in request.GET:
        siteData['controls'] = getTimesControls(request.GET['race_id'])
    else:
        siteData['controls'] = getTimesControls()
    siteData['times'] = getRaceResultsTableContent()

    # notifications
    ## TODO ##
    # move this to getSiteData()
    last = None
    started = None
    for times in siteData['times']:
        for r in times['races']:
            if not started and r['status'] == 'started':
                started = r['desc']
            elif r['status'] == 'finished':
                last = r['desc']
    menu = [item for item in siteData['menu'] if item['id'] == 'times'][0]
    if started is not None:
        menu['notifications'].append(
            {
                'level': 'warning',
                'count': started
            }
        )
    elif last is not None:
        menu['notifications'].append(
            {
                'level': 'success',
                'count': last
            }
        )

    # handle POST requests
    if request.method == "POST":
        if 'refresh_times' in request.POST:
            selected_race = siteData['controls']['selected_race']
            for lane in selected_race['lanes']:
                race_time = 0.0
                try:
                    race_time = float(request.POST['lane_time_min_' + lane['lane']]) * 60.0
                except:
                    pass
                try:
                    race_time += float(request.POST['lane_time_sec_' + lane['lane']])
                except:
                    pass
                try:
                    race_time += float(request.POST['lane_time_hnd_' + lane['lane']]) / 100.0
                except:
                    pass

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
                if team and attendee and race_time != attendee.time:
                    attendee.time = race_time
                    attendee.save()

                    # create finals or ascend winner from the last race
                    populateFinals(attendee)

            # decide which race to edit next
            if 'race_id' in request.GET:
                attendees = RaceAssign.objects.filter(race_id = request.GET['race_id'])
                if any(attendee.time == 0.0 for attendee in attendees):
                    return redirect('/times?race_id={}'.format(request.GET['race_id']))
            return redirect('/times')

        elif 'race_select' in request.POST and request.POST['race_select']:
            race = Race.objects.get(name = request.POST['race_select'])
            if race:
                return redirect('/times?race_id={}'.format(race.id))

    return render(request, 'times.html', siteData)

def results(request):
    # handle login/logout
    loginUser(request)

    if not config.activateResults and not request.user.is_authenticated:
        return redirect('/')

    siteData = getSiteData('results', request.user)
    siteData['results'] = getRaceResultsTableContent()
    return render(request, 'results.html', siteData)

def display(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated:
        return redirect('/')

    siteData = getSiteData('display', request.user)
    siteData['display'] = {
        'timetable': getCurrentTimeTable()
    }

    if raceBlockStarted('{}{}-'.format(config.heatPrefix, 1)):
        siteData['display']['rankings'] = getRankingTable()

    return render(request, 'display.html', siteData)

def settings(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated:
        return redirect('/')

    siteData = getSiteData('settings', request.user)
    siteData['controls'] = getMainSettings()

    if request.method == "POST":
        if 'eventTitle' in request.POST:
            config.siteName = request.POST['eventTitle']
        elif 'eventDate' in request.POST:
            config.eventDate = date.fromisoformat(request.POST['eventDate'])
        elif 'durationMonitorSlide' in request.POST:
            config.displayInterval = float(request.POST['durationMonitorSlide']) * 1e3
        elif 'activateResults' in request.POST:
            config.activateResults = request.POST['activateResults'] == 'on'
        elif 'ownerName' in request.POST:
            config.ownerName = request.POST['ownerName']
        elif 'sponsorName' in request.POST:
            config.sponsorName = request.POST['sponsorName']
        elif 'ownerUrl' in request.POST:
            config.ownerUrl = request.POST['ownerUrl']
        elif 'sponsorUrl' in request.POST:
            config.sponsorUrl = request.POST['sponsorUrl']
        elif 'ownerLogo' in request.POST:
            config.ownerLogo = request.POST['ownerLogo']
        elif 'sponsorLogo' in request.POST:
            config.sponsorLogo = request.POST['sponsorLogo']
        elif 'resetFinals' in request.POST:
            clearFinals()
            populateFinals()
        elif 'resetHeats' in request.POST:
            clearHeatTimes()
        return redirect('/settings')

    return render(request, 'settings.html', siteData)

def djadmin(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated and not request.user.is_superuser:
        return redirect('/')

    siteData = getSiteData('djadmin', request.user)
    siteData['url'] = "/admin"
    response = render(request, 'djadmin.html', siteData)
    response['Content-Security-Policy'] = "frame-ancestors 'self' http://127.0.0.1:1080"
    return response