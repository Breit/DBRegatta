from django.shortcuts import render, redirect
from django.db.models import Q

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

    # handle menu folding
    if toggleFoldMenu(request):
        return redirect('/teams')

    siteData = getSiteData('teams', request.user)
    siteData['content'] = getTeamContent()

    if request.method == 'POST':
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
            try:
                team = Team.objects.get(id = request.GET['edit_id'])
            except:
                team = None
            if team:
                siteData['content']['forms']['mod'] = True
                siteData['content']['forms']['form'] = TeamForm(instance = team)
                siteData['content']['forms']['id'] = team.id

    return render(request, 'teams.html', siteData)

def trainings(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated:
        return redirect('/')

    # handle menu folding
    if toggleFoldMenu(request):
        return redirect('/trainings')

    siteData = getSiteData('trainings', request.user)
    siteData['content'] = {}
    return render(request, 'trainings.html', siteData)

def skippers(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated:
        return redirect('/')

    # handle menu folding
    if toggleFoldMenu(request):
        return redirect('/skippers')

    siteData = getSiteData('skippers', request.user)
    siteData['content'] = {
        'skipperList': getSkipperList()
    }

    if request.method == 'POST':
        if 'show_add_form' in request.POST:
            siteData['content']['skipperForm'] = SkipperForm()
        elif 'add_skipper' in request.POST:
            newSkipper = SkipperForm(request.POST)
            if newSkipper.is_valid():
                newSkipper.save()
                return redirect('/skippers')
            else:
                oldSkipper = Skipper.objects.get(name = request.POST['name'])
                if oldSkipper:
                    for f in oldSkipper._meta.fields:
                        if f.name == 'id':
                            continue
                        setattr(oldSkipper, f.name, getattr(newSkipper.instance, f.name))
                    oldSkipper.save()
                    return redirect('/skippers')
        elif 'delete_skipper' in request.POST:
            skipper = Skipper.objects.get(id = request.POST['delete_skipper'])
            if skipper:
                skipper.delete()
                return redirect('/skippers')
        elif 'activate_skipper' in request.POST:
            skipper = Skipper.objects.get(id = request.POST['activate_skipper'])
            if skipper:
                skipper.active = not skipper.active
                skipper.save()
                return redirect('/skippers')
        elif 'edit_skipper' in request.POST:
            try:
                skipper = Skipper.objects.get(id = request.POST['edit_skipper'])
            except:
                skipper = None
            if skipper:
                return redirect('/skippers?edit_id={}'.format(request.POST['edit_skipper']))
    elif 'edit_id' in request.GET:
        try:
            skipper = Skipper.objects.get(id = int(request.GET['edit_id']))
        except:
            skipper = None
        if skipper:
            siteData['content']['skipperForm'] = SkipperForm(instance=skipper)
            siteData['content']['skipperForm_id'] = skipper.id

    return render(request, 'skippers.html', siteData)

def timetable(request):
    # handle login/logout
    loginUser(request)

    # handle menu folding
    if toggleFoldMenu(request):
        return redirect('/timetable')

    # construct site
    siteData = getSiteData('timetable', request.user)
    siteData['timetable'] = getTimeTableContent()

    if request.user.is_authenticated:
        siteData['controls'] = getTimeTableSettings()

        if request.method == 'POST':
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

    # handle menu folding
    if toggleFoldMenu(request):
        return redirect('/times')

    # shortcut to URL with specific race_id
    if request.method == 'POST' and 'race_select' in request.POST:
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
    siteData['times'] = getRaceResultsTableContent(heatsRankings = False, finalRanks = False)

    # handle POST requests
    if request.method == 'POST':
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

                try:
                    skipper = Skipper.objects.get(
                        name = request.POST['skipper_select_' + lane['lane']]
                    )
                except:
                    skipper = None
                attendee = RaceAssign.objects.get(
                    id = lane['id'],
                    lane = lane['lane'],
                    race_id = selected_race['id']
                )

                # get other lanes to check if the skipper is alreeady used
                if skipper is not None:
                    attendees = RaceAssign.objects.filter(
                        ~Q(id = lane['id']),
                        race_id = selected_race['id']
                    )
                    for other_attendee in attendees:
                        if other_attendee.skipper_id == skipper.id:
                            skipper = None
                            break

                # sanity check for the right team
                team = Team.objects.get(
                    id=attendee.team_id,
                    name=lane['team']
                )

                if team and attendee:
                    save = False
                    if skipper and attendee.skipper_id != skipper.id:
                        save = True
                    elif skipper is None and attendee.skipper_id is not None:
                        save = True
                    elif attendee.time != race_time:
                        save = True
                    if save:
                        attendee.time = race_time
                        attendee.skipper_id = skipper.id if skipper else None
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

    # handle menu folding
    if toggleFoldMenu(request):
        return redirect('/results')

    siteData = getSiteData('results', request.user)
    siteData['results'] = getRaceResultsTableContent(heatsRankings = raceBlockStarted(config.heatPrefix), finalRanks = raceBlockStarted(config.finalPrefix))
    return render(request, 'results.html', siteData)

def display(request):
    # handle login/logout
    loginUser(request)

    # allow display for unauthenticated users
    if not config.anonymousMonitor and not request.user.is_authenticated:
        return redirect('/')

    # handle menu folding
    if toggleFoldMenu(request):
        return redirect('/display')

    siteData = getSiteData('display', request.user)
    siteData['display'] = []

    if not raceBlockFinished(config.finalPrefix):
        timetables = getCurrentTimeTable()
        for timetable in timetables:
            siteData['display'].append(
                {
                    'type': 'timetable',
                    'data': timetable
                }
            )

    if raceBlockFinished(config.finalPrefix):
        siteData['display'].append(getFinalRankings())          # show finale rankings if finale has finished
    else:
        if raceBlockStarted(config.heatPrefix):
            siteData['display'].append(getHeatRankings())       # show heats rankings only if finale is not finished

    return render(request, 'display.html', siteData)

def settings(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated:
        return redirect('/')

    # handle menu folding
    if toggleFoldMenu(request):
        return redirect('/settings')

    siteData = getSiteData('settings', request.user)
    siteData['controls'] = getMainSettings()
    siteData['lastBackup'] = getLastDataBaseBackup()

    if request.method == 'POST':
        if 'eventTitle' in request.POST:
            config.siteName = request.POST['eventTitle']
        elif 'eventDate' in request.POST:
            config.eventDate = date.fromisoformat(request.POST['eventDate'])
        elif 'durationMonitorSlide' in request.POST:
            config.displayInterval = int(float(request.POST['durationMonitorSlide']) * 1e3)
        elif 'displayDataRefresh' in request.POST:
            config.displayDataRefresh = int(float(request.POST['displayDataRefresh']) * 1e3)
        elif 'maxRacesPerPage' in request.POST:
            config.maxRacesPerPage = int(request.POST['maxRacesPerPage'])
        elif 'activateResults' in request.POST:
            config.activateResults = request.POST['activateResults'] == 'on'
        elif 'anonymousMonitor' in request.POST:
            config.anonymousMonitor = request.POST['anonymousMonitor'] == 'on'
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
        elif 'siteDomain' in request.POST:
            config.domain = request.POST['siteDomain']
        elif 'liveResultsHint' in request.POST:
            config.liveResultsHint = request.POST['liveResultsHint']
        elif 'resetFinals' in request.POST:
            clearFinals()
            populateFinals()
        elif 'resetHeats' in request.POST:
            clearHeatTimes()
        elif 'backupDatabase' in request.POST:
            backupDataBase()
        elif 'resetTeams' in request.POST:
            # TODO
            pass
        elif 'resetSkippers' in request.POST:
            # TODO
            pass
        elif 'displayOverscan' in request.POST:
            config.overscan = int(request.POST['displayOverscan'])
        return redirect('/settings')

    return render(request, 'settings.html', siteData)

def djadmin(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated and not request.user.is_superuser:
        return redirect('/')

    # handle menu folding
    if toggleFoldMenu(request):
        return redirect('/djadmin')

    siteData = getSiteData('djadmin', request.user)
    siteData['url'] = "/admin"
    response = render(request, 'djadmin.html', siteData)
    response['Content-Security-Policy'] = "frame-ancestors 'self' http://127.0.0.1:1080"
    return response

def impressum(request):
    # handle login/logout
    loginUser(request)

    # handle menu folding
    if toggleFoldMenu(request):
        return redirect('/impressum')

    siteData = getSiteData('impressum', request.user)
    siteData['impressum'] = getImpressumData()

    return render(request, 'impressum.html', siteData)