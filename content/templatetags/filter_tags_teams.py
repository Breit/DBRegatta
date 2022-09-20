from django import template

register = template.Library()

'''
Definition of a filter for the teams list to filter only active teams.
'''
@register.filter
def active_teams(teams):
    active_teams = []

    try:
        for team in teams:
            if 'active' in team and 'wait' in team and team['active'] and not team['wait']:
                active_teams.append(team)
    except:
        pass

    return active_teams

'''
Definition of a filter for the teams list to filter only active teams on the waitlist.
'''
@register.filter
def waitlist_teams(teams):
    active_teams = []

    try:
        for team in teams:
            if 'active' in team and 'wait' in team and team['active'] and team['wait']:
                active_teams.append(team)
    except:
        pass

    return active_teams

'''
Definition of a filter for the teams list to filter only inactive teams.
'''
@register.filter
def inactive_teams(teams):
    active_teams = []

    try:
        for team in teams:
            if 'active' in team and not team['active']:
                active_teams.append(team)
    except:
        pass

    return active_teams