from django.shortcuts import render, redirect
from django.db.models import Q
from django.http.response import HttpResponseRedirect

from .views_helper import *

def handler404(request, *args, **kwargs):
    return HttpResponseRedirect('/')

def main(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated:
        if raceBlockFinished(config.finalPrefix):
            return redirect('/results')
        else:
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
        # submit a new team
        if 'add_team' in request.POST:
            newTeamForm = TeamForm(request.POST)
            if Team.objects.filter(name=request.POST['name']).exists():
                siteData['content']['form'] = newTeamForm
            if newTeamForm['date'].data == '':
                siteData['content']['form'] = newTeamForm
                newTeamForm.add_error('date', 'Date missing')
            elif newTeamForm.is_valid():
                newTeamForm.save()
                return redirect('/teams')

        # toggle team activation
        elif 'activate_team' in request.POST:
            try:
                modTeam = Team.objects.get(id = request.POST['activate_team'])
            except:
                modTeam = None
            if modTeam:
                modTeam.active = not modTeam.active
                modTeam.wait = modTeam.active
                modTeam.save()
            return redirect('/teams')

        # toggle team waitlist
        elif 'waitlist_team' in request.POST:
            try:
                modTeam = Team.objects.get(id = request.POST['waitlist_team'])
            except:
                modTeam = None
            if modTeam:
                modTeam.wait = not modTeam.wait
                if modTeam.wait:
                    modTeam.active = True
                modTeam.save()
            return redirect('/teams')

        # delete team from database
        elif 'delete_team' in request.POST:
            try:
                delTeam = Team.objects.get(id = request.POST['delete_team'])
            except:
                delTeam = None
            if delTeam:    # also delete all race assignements with the team as well
                assignments = RaceAssign.objects.filter(team_id=delTeam.id)
                for assignment in assignments:
                    assignment.delete()
                delTeam.delete()
            return redirect('/teams')

        # show edit team form
        elif 'edit_team' in request.POST:
            try:
                modTeam = Team.objects.get(id = request.POST['edit_team'])
            except:
                modTeam = None
            if modTeam:
                siteData['content']['form'] = TeamForm(instance = modTeam)

        # submit_mod_team
        elif 'mod_team' in request.POST:
            try:
                modTeam = Team.objects.get(id = request.POST['mod_team'])
            except:
                modTeam = None
            if modTeam:
                modTeamForm = TeamForm(
                    request.POST,
                    instance = modTeam
                )
                if modTeamForm.is_valid():
                    modTeamForm.save()
                    return redirect('/teams')
                else:
                    siteData['content']['form'] = modTeamForm

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
    siteData['content'] = {
        'trainingsList': getTrainingsList(),
        'countTrainings': Training.objects.filter().count(),
        'countTeams': Training.objects.filter().count(),
        'countSkippers': Training.objects.filter().count(),
        'trainingForm': TrainingForm()
    }
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
        'skipperList': getSkipperList(),
        'activeSkippers': Skipper.objects.filter(active = True).count(),
        'inactiveSkippers': Skipper.objects.filter(active = False).count(),
        'skipperForm': SkipperForm()
    }

    if request.method == 'POST':
        if 'add_skipper' in request.POST:
            newSkipper = SkipperForm(request.POST)
            if Skipper.objects.filter(name=request.POST['name']).exists():
                siteData['content']['skipperForm'] = newSkipper
            elif newSkipper.is_valid():
                newSkipper.save()
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
                siteData['content']['skipperForm'] = SkipperForm(instance=skipper)
        elif 'mod_skipper' in request.POST:
            try:
                skipper = Skipper.objects.get(id = request.POST['mod_skipper'])
            except:
                skipper = None
            if skipper:
                skipperForm = SkipperForm(
                    request.POST,
                    instance = skipper
                )
                if skipperForm.is_valid():
                    skipperForm.save()
                    return redirect('/skippers')
                else:
                    siteData['content']['skipperForm'] = skipperForm

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
            elif 'createTimetable' in request.POST:
                createTimeTable()
            return redirect('/timetable')

    try:
        post = Post.objects.get(site='timetable')
        if request.user.is_authenticated:
            siteData['post'] = post.content
            siteData['post_disabled'] = not post.enable
        elif post.enable:
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

    # construct site data
    siteData = getSiteData('times', request.user)
    siteData['times'] = getRaceResultsTableContent(heatsRankings = False, finalRanks = False)
    siteData['data'] = getTimesData()

    # handle POST requests
    if request.method == 'POST':
        if 'race_name' in request.POST:
            attendees = None
            try:
                race = Race.objects.get(name=request.POST['race_name'])
                attendees = RaceAssign.objects.filter(race_id=race.id)
            except:
                pass
            for attendee in attendees:
                race_time = 0.0
                try:
                    race_time = float(request.POST['lane_time_min_' + attendee.lane]) * 60.0
                except:
                    pass
                try:
                    race_time += float(request.POST['lane_time_sec_' + attendee.lane])
                except:
                    pass
                try:
                    race_time += float(request.POST['lane_time_hnd_' + attendee.lane]) / 100.0
                except:
                    pass

                try:
                    skipper = Skipper.objects.get(
                        name = request.POST['skipper_select_' + attendee.lane]
                    )
                except:
                    skipper = None

                # get other lanes to check if the skipper is already used
                if skipper is not None:
                    attendees_check = RaceAssign.objects.filter(
                        ~Q(id = attendee.id),
                        race_id = attendee.race_id
                    )
                    for other_attendee in attendees_check:
                        if other_attendee.skipper_id == skipper.id:
                            skipper = None
                            break

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

            return redirect('/times')

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
        elif 'refreshTimes' in request.POST:
            updateTimeTable()
        elif 'resetFinals' in request.POST:
            clearFinals()
            populateFinals()
        elif 'resetHeats' in request.POST:
            clearHeatTimes()
        elif 'resetTimetable' in request.POST:
            clearRaces()
        elif 'backupDatabase' in request.POST:
            backupDataBase()
        elif 'resetTeams' in request.POST:
            clearTeams()
        elif 'resetSkippers' in request.POST:
            clearSkippers()
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