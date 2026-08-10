import csv
from constance import config
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import redirect
from django.db.models import F

from .views_helper import *

def teams(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated:
        return redirect('/')

    # Provide a filename for the CSV
    filename = '{at}_{abbr}_teams.csv'.format(
        at=datetime.now().strftime("%Y%m%d-%H%M%S"),
        abbr=config.siteAbbr
    )

    # Gather categories, including a virtual one for teams without a category
    categories = list(Category.objects.all())
    if len(Team.objects.filter(category_id=None)) > 0:
        categories.append(Category())

    hasCategories = len(categories) > 1

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

    # Prepend a BOM so spreadsheet apps detect UTF-8 correctly
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')

    header = []
    if hasCategories:
        header.append(config.placeholderCategoryName)
    header.extend([
        config.activeTeams,
        config.teamTableHeaderID,
        config.teamTableHeaderTeam,
        config.teamTableHeaderCompany,
        config.placeholderTeamCaptain,
        config.teamTableHeaderEmail,
        config.teamTableHeaderPhone,
        config.teamTableHeaderAddress,
        config.teamTableHeaderPosition,
        config.teamTableHeaderDate,
    ])
    writer.writerow(header)

    statusFilters = [
        (config.activeTeams,   {'active': True,  'wait': False}),
        (config.waitlistTeams, {'active': True,  'wait': True}),
        (config.inactiveTeams, {'active': False}),
    ]

    for category in categories:
        categoryName = category.name if category.id is not None else config.raceCategoryEmptyName
        for status, teamFilter in statusFilters:
            teamList = Team.objects.filter(
                category_id=category.id,
                **teamFilter
            ).order_by(
                F('position').asc(nulls_last=True)
            )
            for i, team in enumerate(teamList):
                row = []
                if hasCategories:
                    row.append(categoryName)
                row.extend([
                    status,
                    i + 1,
                    team.name,
                    team.company,
                    team.contact,
                    team.email,
                    team.phone,
                    team.address.replace('\r\n', ', ').replace('\n', ', '),
                    team.position if team.position is not None else '',
                    team.date.strftime('%d.%m.%Y') if team.date is not None else '',
                ])
                writer.writerow(row)

    return response
