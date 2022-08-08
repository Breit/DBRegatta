from django.shortcuts import render, redirect
from django.forms.models import model_to_dict

from .views_main import getSiteData

from .models import Team
from .forms import TeamForm

# settings for the teams page
def getTeamSettings():
    settings = {
        'editTeamHeader': 'Bearbeitung Teams',
        'teamListHeader': 'Teamliste',
        'activeTeams': 'Aktive Teams',
        'addTeam': 'Neues Team',
        'submitAddTeam': 'Hinzufügen',
        'submitEditTeam': 'Speichern',
        'submitAbort': 'Abbrechen',
        'warningDeleteTeam': 'Team endgültig löschen?',
        'addTeamIcon': 'add.svg',
        'removeTeamIcon': 'trash.svg',
        'activeTeamIcon': 'active.svg',
        'inactiveTeamIcon': 'inactive.svg',
        'editTeamIcon': 'edit.svg',
        'submitTeamIcon': 'ok.svg',
        'cancelTeamIcon': 'cancel.svg',
        'checkedTeamIcon': 'checked.svg',
        'uncheckedTeamIcon': 'unchecked.svg'
    }
    return settings

# get teams list from database
def getTeamContent():
    content = { 'teams': [] }
    for team in Team.objects.all():
        content['teams'].append(model_to_dict(team))
    content['activeTeams'] = Team.objects.filter(active=True).count()
    content['totalTeams'] = Team.objects.all().count()
    content['forms'] = {
        'form': TeamForm(),
        'add': False,
        'mod': False
    }
    return content

def teams(request):
    # if user not in authenticated_users:
    #    return redirect('/')
    
    siteData = {}
    siteData['settings'] = getSiteData()
    siteData['settings']['navigationCSS'] = 'menu.css'
    siteData['settings']['pageCSS'] = 'teams.css'
    siteData['settings'].update(getTeamSettings())
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
            if newTeamForm.is_valid():                
                newTeamForm.save()
                siteData['content'] = getTeamContent()              # refresh from DB
                return redirect('/teams')
        
        # abort submitting teams changes
        elif 'cancel_team' in request.POST:
            siteData['content']['forms']['add'] = False
            siteData['content']['forms']['mod'] = False
            return redirect('/teams')
        
        # toggle team activation
        elif 'activate_team' in request.POST:
            if Team.objects.filter(name=request.POST['activate_team']).exists():
                modTeam = Team.objects.get(name=request.POST['activate_team'])
                modTeam.active = not modTeam.active
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
    else:  # handle request.GET
        # prepare form for modifying a team
        if 'edit_id' in request.GET:
            if Team.objects.filter(id = request.GET['edit_id']).exists():
                siteData['content']['forms']['mod'] = True
                siteData['content']['forms']['form'] = TeamForm(
                    instance = Team.objects.get(id = request.GET['edit_id'])
                )
    
    return render(request, 'teams.html', siteData)