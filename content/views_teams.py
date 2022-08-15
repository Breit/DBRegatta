# import datetime
from django.shortcuts import render, redirect
from django.forms.models import model_to_dict

from .views_main import getSiteData

from .models import Team
from .forms import TeamForm

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

            # try:
            #     datetime.datetime.strptime(newTeamForm['date'].data, "%Y-%m-%d")
            # except ValueError:
            #     newTeamForm.add_error('date', 'Date missing')

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