from django.shortcuts import render, redirect

from .views_helper import *

def main(request):
    return render(request, 'main.html', getSiteData())

def teams(request):
    # if user not in authenticated_users:
    #    return redirect('/')

    siteData = getSiteData('teams')
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
    siteData = getSiteData('trainings')
    siteData['content'] = {}
    return render(request, 'trainings.html', siteData)

def timetable(request):
    siteData = getSiteData('timetable')
    siteData['timetable'] = getTimeTableContent()
    siteData['controls'] = getTimeTableSettings()

    if request.method == "POST":
        if 'timeBegin' in request.POST:
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
        elif 'create_timetable' in request.POST:
            createTimeTable()
        elif 'refresh_times' in request.POST:
            updateTimeTable()
        return redirect('/timetable')

    return render(request, 'timetable.html', siteData)

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
                try:
                    time = float(request.POST['lane_time_min_' + lane['lane']]) * 60.0
                except:
                    pass
                try:
                    time += float(request.POST['lane_time_sec_' + lane['lane']])
                except:
                    pass
                try:
                    time += float(request.POST['lane_time_hnd_' + lane['lane']]) / 100.0
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
                if team and attendee and time != attendee.time:
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

def results(request):
    siteData = getSiteData('results')
    siteData['results'] = getRaceResultsTableContent()
    return render(request, 'results.html', siteData)

def display(request):
    siteData = getSiteData('display')
    siteData['display'] = {
        'timetable': getCurrentTimeTable(),
        'rankings': getRankingTable()
    }

    return render(request, 'display.html', siteData)

def settings(request):
    siteData = getSiteData('settings')
    siteData['controls'] = getMainSettings()

    if request.method == "POST":
        if 'eventTitle' in request.POST:
            config.siteName = request.POST['eventTitle']
        elif 'eventDate' in request.POST:
            config.eventDate = date.fromisoformat(request.POST['eventDate'])
        elif 'durationMonitorSlide' in request.POST:
            config.displayInterval = float(request.POST['durationMonitorSlide']) * 1e3
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
        return redirect('/settings')

    return render(request, 'settings.html', siteData)

def djadmin(request):
    siteData = getSiteData('djadmin')
    siteData['url'] = "/admin"
    response = render(request, 'djadmin.html', siteData)
    response['Content-Security-Policy'] = "frame-ancestors 'self' http://127.0.0.1:1080"
    return response