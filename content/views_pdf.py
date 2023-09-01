import io
from constance import config
from datetime import datetime

from django.http import FileResponse
from django.shortcuts import redirect
from django.db.models import F

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, LongTable, TableStyle, PageBreak, Spacer, TopPadder

from .views_helper import *
from .pdf_helper import *
from .templatetags.filter_tags import asTime

def teams(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated:
        return redirect('/')

    # Provide a filename for the PDF
    filename = '{at}_{abbr}_teams.pdf'.format(
        at=datetime.now().strftime("%Y%m%d-%H%M%S"),
        abbr=config.siteAbbr
    )

    # Define styling
    styles = pdfStyleSheet()
    mainTableStyle = TableStyle([
        ('BOX',             (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # border for whole table
        ('LINEABOVE',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # top border for each row
        ('LINEBELOW',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # bottom border for each row
        ('LINEBELOW',       (0,  1), (-1,  1), 0.5 , colors.grey),                          # line under colum header row
        ('SPAN',            (0,  0), (-1,  0)),                                             # span title row (1st row)
        ('SPAN',            (4,  1), ( 5,  1)),                                             # span signup columns
        ('VALIGN',          (0,  2), ( 0, -1), 'MIDDLE'),                                   # id middle-aligned
        ('VALIGN',          (1,  2), ( 3, -1), 'TOP'),                                      # team, contact and address top-aligned
        ('VALIGN',          (4,  2), ( 5, -1), 'MIDDLE'),                                   # signup centered
        ('ROWBACKGROUNDS',  (0,  0), (-1, -1), (colors.whitesmoke, colors.transparent)),    # alternate row coloring
    ])
    statTableStyle = TableStyle([
        ('BOX',             (0,  0), (-1, -1), 0.25, colors.lightgrey),
        ('GRID',            (0,  0), (-1, -1), 0.25, colors.lightgrey),
        ('BOTTOMPADDING',   (0,  0), (-1, -1), 6),
        ('TOPPADDING',      (0,  0), (-1, -1), 6),
    ])

    # Gather data
    teamTableData = []
    categories = Category.objects.all()
    if len(categories) == 0:
        # Workaround for no categories
        categories = [Category()]
        categories[-1].name = ''
        categories[-1].tag = ''
    for category in categories:
        teamTableData.append(
            {
                # Active Teams
                'header': Paragraph(
                    '{header} {status}{cat}'.format(
                        header=config.teamTableHeaderTeams,
                        status=config.activeTeams,
                        cat=' - {}'.format(category.name) if len(categories) > 1 else ''
                    ),
                    styles['TableHeader']
                ),
                'data': Team.objects.filter(
                    active=True,
                    wait=False,
                    category_id=category.id
                ).order_by(
                    F('position').asc(nulls_last=True)
                )
            }
        )
        teamTableData.append(
            {
                # Waitlist Teams
                'header': Paragraph(
                    '{header} {status}{cat}'.format(
                        header=config.teamTableHeaderTeams,
                        status=config.waitlistTeams,
                        cat=' - {}'.format(category.name) if len(categories) > 1 else ''
                    ), styles['TableHeader']
                ),
                'data': Team.objects.filter(
                    active=True,
                    wait=True,
                    category_id=category.id
                ).order_by(
                    F('position').asc(nulls_last=True)
                )
            }
        )
        teamTableData.append(
            {
                # Inactive Teams
                'header': Paragraph(
                    '{header} {status}{cat}'.format(
                        header=config.teamTableHeaderTeams,
                        status=config.inactiveTeams,
                        cat=' - {}'.format(category.name) if len(categories) > 1 else ''
                    ), styles['TableHeader']
                ),
                'data': Team.objects.filter(
                    active=False,
                    category_id=category.id
                ).order_by(
                    F('position').asc(nulls_last=True)
                )
            }
        )

    # Table column header is the same for all tables
    tableColumnHeader = [
        Paragraph('{id}'.format(id=config.teamTableHeaderID), styles['ColumnHeaderC']),
        Paragraph('{team} / {company}'.format(team=config.teamTableHeaderTeam, company=config.teamTableHeaderCompany), styles['ColumnHeader']),
        Paragraph('{contact}'.format(contact=config.placeholderTeamCaptain), styles['ColumnHeader']),
        Paragraph('{address}'.format(address=config.teamTableHeaderAddress), styles['ColumnHeader']),
        Paragraph('{position}'.format(position=config.teamTableHeaderPosition), styles['ColumnHeaderC']),
        Paragraph('{date}'.format(date=config.teamTableHeaderDate), styles['ColumnHeaderC'])
    ]

    # Start story with front page
    story = [
        Spacer(width=0, height=20*mm),
        Paragraph('{event}'.format(event=config.siteName), styles['Title']),
        Paragraph('{date}'.format(date=config.eventDate.strftime('%d. %B %Y')), styles['SubTitle']),
        Spacer(width=0, height=20*mm),
        Paragraph('{teamList}'.format(teamList=config.teamListHeader), styles['Title'])
    ]

    # Statistics section
    statTableData = []

    if len(categories) > 1:
        # Statistics for all race categories/classes
        statTableCols = (90*mm, 30*mm, 30*mm, 30*mm)
        statTableData.append(
            [
                None,
                Paragraph('{type}'.format(type=config.activeTeams), styles['TableHeaderC']),
                Paragraph('{type}'.format(type=config.waitlistTeams), styles['TableHeaderC']),
                Paragraph('{type}'.format(type=config.inactiveTeams), styles['TableHeaderC'])
            ]
        )
        cat_data = []
        c = 0
        for i in range(len(teamTableData)):
            if len(cat_data) == 0:
                cat_data.append(
                    Paragraph(
                        '{header}: {cat}'.format(
                            header=config.placeholderCategoryName,
                            cat=categories[c].name
                        ),
                        styles['TableHeader']
                    )
                )
                c += 1
            cat_data.append(
                Paragraph(
                    '{data}'.format(
                        data=teamTableData[i]['data'].count()
                    ),
                    styles['TableHeaderBC']
                )
            )
            if i > 0 and (i + 1) % 3 == 0:
                statTableData.append(cat_data)
                cat_data = []
    else:
        # Only global statistics, no categories/classes
        statTableCols = (130*mm, 50*mm)
        for teamTable in teamTableData:
            statTableData.append(
                [
                    teamTable['header'],
                    Paragraph('{count}'.format(count=len(teamTable['data'])), styles['TableHeaderBC']),
                ]
            )

    statTable = Table(
        statTableData,
        style=statTableStyle,
        colWidths=statTableCols
    )
    story.append(
        TopPadder(
            Table(
                [
                    [statTable],
                    [Spacer(width=0, height=10*mm)]
                ]
            )
        )
    )
    story.append(PageBreak())

    # Main tables
    for teamTable in teamTableData:
        tableData = [
            [
                teamTable['header']
            ],
            tableColumnHeader
        ]
        for i, team in enumerate(teamTable['data']):
            teamRow = []
            teamRow.append(
                Paragraph('{id}'.format(id=(i + 1)), styles['NormalC'])
            )
            teamRow.append(
                [
                    Paragraph('{name}'.format(name=team.name), styles['NormalB']),
                    Paragraph('{company}'.format(company=team.company), styles['Secondary'])
                ]
            )
            teamRow.append(
                [
                    Paragraph('{contact}'.format(contact=team.contact), styles['NormalB']),
                    Paragraph('<a href="mailto:{email}">{email}</a>'.format(email=team.email), styles['SecondaryLink']),
                    Paragraph('{phone}'.format(phone=team.phone), styles['Secondary'])
                ]
            )
            teamRow.append(
                Paragraph('{address}'.format(address=team.address if team.address is not None else ''), styles['Normal'])
            )
            teamRow.append(
                Paragraph('{position}'.format(position=team.position if team.position is not None else ''), styles['NormalC'])
            )
            teamRow.append(
                Paragraph('{date}'.format(date=team.date.strftime('%d.%m.%Y') if team.date is not None else ''), styles['NormalC'])
            )
            tableData.append(teamRow)

        story.append(
            LongTable(
                tableData,
                style=mainTableStyle,
                repeatRows=2,
                colWidths=(10*mm, 50*mm, 50*mm, 38*mm, 10*mm, 22*mm)
            )
        )

        # Insert a page break for new tables
        story.append(PageBreak())

    # Create a file-like buffer to receive PDF data
    pdf_buffer = io.BytesIO()

    # Create document
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        leftMargin=15*mm,
        rightMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=20*mm
    )
    doc.title = filename
    doc.creator = config.ownerName
    doc.author = config.ownerName
    doc.subject = config.siteName
    doc.keywords = [config.siteAbbr, config.teamListHeader]

    doc.build(story, canvasmaker=PageNumCanvas)

    pdf_buffer.seek(0)

    # FileResponse sets the Content-Disposition header (as_attachment=True)
    # so that browsers present the option to save the file
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)

def timetable(request):
    # handle login/logout
    loginUser(request)

    # Provide a filename for the PDF
    filename = '{at}_{abbr}_timetable.pdf'.format(
        at=datetime.now().strftime("%Y%m%d-%H%M%S"),
        abbr=config.siteAbbr
    )

    finaleRunning = getCurrentRaceBlock() == config.finalPrefix

    # Define styling
    styles = pdfStyleSheet()
    mainTableStyle = TableStyle([
        ('SPAN',            (1,  0), (-1,  0)),                                             # span header row for each table
        ('BOX',             (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # border for whole table
        ('LINEABOVE',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # top border for each row
        ('LINEBELOW',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # bottom border for each row
        ('VALIGN',          (0,  0), (-1, -1), 'MIDDLE'),                                   # all cells middle-aligned
        ('ROWBACKGROUNDS',  (0,  0), (-1, -1), (colors.whitesmoke, colors.transparent)),    # alternate row coloring
    ])
    subTableHeaderStyle = TableStyle([
        ('BOTTOMPADDING',   (0,  0), (-1, -1), 0),
        ('TOPPADDING',      (0,  0), (-1, -1), 0)
    ])
    subTableStyle = TableStyle([
        ('BOTTOMPADDING',   (0,  0), (-1, -1), 3),
        ('TOPPADDING',      (0,  0), (-1, -1), 3),
        ('VALIGN',          (0,  0), (-1, -1), 'MIDDLE')
    ])
    subTableStyleFinale = TableStyle([
        ('BOTTOMPADDING',   (0,  0), (-1, -1), 3 if finaleRunning else 0),
        ('TOPPADDING',      (0,  0), (-1, -1), 3 if finaleRunning else 0),
        ('VALIGN',          (0,  0), (-1, -1), 'MIDDLE')
    ])
    if (config.boardingTime.seconds > 0):
        subTableColumns = (12*mm, 52*mm, 65*mm)
        mainTableColumns = (18*mm, 18*mm, 15*mm, sum(subTableColumns))
    else:
        subTableColumns = (12*mm, 50*mm, 62*mm, 23*mm)
        mainTableColumns = (18*mm, 15*mm, sum(subTableColumns))

    # Gather data
    timetableData = getTimeTableContent()

    # Table column header is the same for all tables
    subTableColumnHeader = []
    subTableColumnHeader.append(Paragraph('{lane}'.format(lane=config.timetableHeaderLane), styles['ColumnHeaderC']))
    subTableColumnHeader.append(Paragraph('{team}'.format(team=config.timetableHeaderTeam), styles['ColumnHeader']))
    subTableColumnHeader.append(Paragraph('{company}'.format(company=config.timetableHeaderCompany), styles['ColumnHeader']))
    if (config.boardingTime.seconds <= 0):          # Hide skipper if boarding time is displayed
        subTableColumnHeader.append(Paragraph('{skipper}'.format(skipper=config.timetableHeaderSkipper), styles['ColumnHeader']))

    tableColumnHeader = []
    if (config.boardingTime.seconds > 0):
        tableColumnHeader.append(Paragraph('{btime}'.format(btime=config.boardingTimeHeader), styles['ColumnHeaderC']))
    tableColumnHeader.append(Paragraph('{time}'.format(time=config.timetableHeaderTime), styles['ColumnHeaderC']))
    tableColumnHeader.append(Paragraph('{race}'.format(race=config.timetableHeaderName), styles['ColumnHeaderC']))
    tableColumnHeader.append(Table([subTableColumnHeader], colWidths=subTableColumns, style=subTableHeaderStyle))

    # Start story with front page
    story = [
        Spacer(width=0, height=20*mm),
        Paragraph('{event}'.format(event=config.siteName), styles['Title']),
        Paragraph('{date}'.format(date=config.eventDate.strftime('%d. %B %Y')), styles['SubTitle']),
        Spacer(width=0, height=20*mm),
        Paragraph('{headline}'.format(headline=config.timetableHeader), styles['Title'])
    ]

    # Post
    postFrameData = []
    try:
        post = Post.objects.get(site='timetable')
        if post.enable:
            for para in markdownStory(post.content):
                postFrameData.append([para])
            postFrameData.append([Spacer(width=0, height=10*mm)])
    except Post.DoesNotExist:
        pass

    if len(postFrameData) > 0:
        story.append(
            TopPadder(
                Table(
                    postFrameData,
                    colWidths=(180*mm)
                )
            )
        )
    story.append(PageBreak())


    # Get team content: active teams
    finaleOnNewPage = True
    for event in timetableData:
        tableData = []
        tableData.append([])
        tableData[-1].append(Paragraph('{time}'.format(time=event['time'].strftime('%H:%M')), styles['TableHeaderBC']))
        tableData[-1].append(Paragraph('{agendum}'.format(agendum=event['desc']), styles['TableHeader']))
        tableData[-1].append(None)
        if (config.boardingTime.seconds > 0):
            tableData[-1].append(None)

        if 'races' in event and len(event['races']) > 0:
            tableData.append(tableColumnHeader)
            for race in event['races']:
                raceRow = []
                if (config.boardingTime.seconds > 0):
                    raceRow.append(
                        Paragraph('{btime}'.format(btime=race['boarding'].strftime('%H:%M')), styles['NormalC'])
                    )
                raceRow.append(
                    Paragraph('{time}'.format(time=race['time'].strftime('%H:%M')), styles['NormalBC'])
                )
                raceRow.append(
                    Paragraph('{racename}'.format(racename=race['desc']), styles['NormalC'])
                )

                # Lanes as sub-table
                laneTable = []
                for lane in race['lanes']:
                    laneRow = []
                    laneRow.append(
                        Paragraph('{racelane}'.format(racelane=lane['lane']), styles['NormalC'])
                    )
                    if 'draw' in lane and lane['draw']:
                        laneRow.append(
                            Paragraph('{team}'.format(team=lane['team']), styles['NormalI'])
                        )
                    else:
                        laneRow.append(
                            Paragraph('{team}'.format(team=lane['team']), styles['NormalB'])
                        )
                    laneRow.append(
                        Paragraph('{company}'.format(company=lane['company']), styles['Secondary'])
                    )
                    if (config.boardingTime.seconds <= 0):
                        laneRow.append(
                            Paragraph('{skipper}'.format(skipper=lane['skipper']['name'] if 'name' in lane['skipper'] else '-'), styles['Normal'])
                        )
                    laneTable.append(laneRow)
                raceRow.append(Table(laneTable, colWidths=subTableColumns, style=subTableStyleFinale if event['type'] == 'finale' else subTableStyle))

                tableData.append(raceRow)

        # Insert a page break before the first finale table
        if finaleOnNewPage and 'type' in event and event['type'] == 'finale':
            story.append(PageBreak())
            finaleOnNewPage = False

        story.append(
            LongTable(
                tableData,
                style=mainTableStyle,
                repeatRows=2,
                spaceBefore=5*mm,
                colWidths=mainTableColumns
            )
        )

    # Create a file-like buffer to receive PDF data
    pdf_buffer = io.BytesIO()

    # Create document
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        leftMargin=15*mm,
        rightMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=20*mm
    )
    doc.title = filename
    doc.creator = config.ownerName
    doc.author = config.ownerName
    doc.subject = config.siteName
    doc.keywords = [config.siteAbbr, config.timetableHeader]

    doc.build(story, canvasmaker=PageNumCanvas)

    pdf_buffer.seek(0)

    # FileResponse sets the Content-Disposition header (as_attachment=True)
    # so that browsers present the option to save the file
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)

def results(request):
    # handle login/logout
    loginUser(request)

    if not config.activateResults and not request.user.is_authenticated:
        return redirect('/')

    # Provide a filename for the PDF
    filename = '{at}_{abbr}_results.pdf'.format(
        at=datetime.now().strftime("%Y%m%d-%H%M%S"),
        abbr=config.siteAbbr
    )

    # Define styling
    styles = pdfStyleSheet()
    mainTableStyle = TableStyle([
        ('BOX',             (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # border for whole table
        ('SPAN',            (0,  0), (-1,  0)),                                             # span table headers
        ('LINEABOVE',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # top border for each row
        ('LINEBELOW',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # bottom border for each row
        ('VALIGN',          (0,  0), (-1, -1), 'MIDDLE'),                                   # all cells middle-aligned
        ('VALIGN',          (0,  1), (-1,  1), 'BOTTOM'),                                   # column header cells bottom-aligned
        ('ROWBACKGROUNDS',  (0,  0), (-1, -1), (colors.whitesmoke, colors.transparent)),    # alternate row coloring
    ])
    subTableHeaderStyle = TableStyle([
        ('BOTTOMPADDING',   (0,  0), (-1, -1), 0),
        ('TOPPADDING',      (0,  0), (-1, -1), 0)
    ])
    subTableStyle = TableStyle([
        ('BOTTOMPADDING',   (0,  0), (-1, -1), 1),
        ('TOPPADDING',      (0,  0), (-1, -1), 1),
        ('VALIGN',          (0,  0), (-1, -1), 'MIDDLE')
    ])

    # Gather data
    resultData = getRaceResultsTableContent(heatsRankings = raceBlockStarted(config.heatPrefix), finalRanks = raceBlockStarted(config.finalPrefix))

    # Start story with front page
    story = [
        Spacer(width=0, height=20*mm),
        Paragraph('{event}'.format(event=config.siteName), styles['Title']),
        Paragraph('{date}'.format(date=config.eventDate.strftime('%d. %B %Y')), styles['SubTitle']),
        Spacer(width=0, height=20*mm),
        Paragraph('{headline}'.format(headline=config.resultsTableHeader), styles['Title']),
        PageBreak()
    ]

    # Get team content: active teams
    for result in resultData:
        tableData = []
        headerRow = [
            Paragraph('{agendum}'.format(agendum=result['desc']), styles['TableHeader'])
        ]

        # Define columns based on result type
        skipResults = False
        if result['type'] == 'heat':
            # Add dummy cells to header based on column count
            headerRow += [None] * 2

            # Define columns
            subTableColumns = (12*mm, 80*mm, 24*mm, 12*mm, 22*mm)
            subTableColumnHeader = [
                Paragraph('{lane}'.format(lane=config.timetableHeaderLane), styles['ColumnHeaderC']),
                Paragraph('{team} / {company}'.format(team=config.timetableHeaderTeam, company=config.timetableHeaderCompany), styles['ColumnHeader']),
                Paragraph('{skipper}'.format(skipper=config.timesHeaderSkipper), styles['ColumnHeader']),
                Paragraph('{place}'.format(place=config.timesHeaderPlace), styles['ColumnHeaderC']),
                Paragraph('{time}'.format(time=config.timesHeaderTime), styles['ColumnHeaderC'])
            ]
            mainTableColumns = (15*mm, 15*mm, sum(subTableColumns))
            tableColumnHeader = [
                Paragraph('{time}'.format(time=config.timetableHeaderTime), styles['ColumnHeaderC']),
                Paragraph('{race}'.format(race=config.timetableHeaderName), styles['ColumnHeaderC']),
                Table([subTableColumnHeader], colWidths=subTableColumns, style=subTableHeaderStyle)
            ]
        elif result['type'] == 'rankingHeats':
            # Don't display individual results if there are more than 3 heats
            hc = len(result['heats']) if 'heats' in result and len(result['heats']) < 4 else 0

            # Add dummy cells to header based on column count
            headerRow += [None] * (2 + hc)

            # Dynamic columns based on heat count
            mainTableColumns = tuple([12*mm] + [50*mm] + [(96 - 17 * hc)*mm] + [17*mm] * hc + [22*mm])
            tableColumnHeader = []
            tableColumnHeader.append(Paragraph('{rank}'.format(rank=config.timesHeaderRank), styles['ColumnHeaderC']))
            tableColumnHeader.append(Paragraph('{team}'.format(team=config.timetableHeaderTeam), styles['ColumnHeader']))
            tableColumnHeader.append(Paragraph('{company}'.format(company=config.timetableHeaderCompany), styles['ColumnHeader']))
            for h in result['heats'] if 'heats' in result and hc > 0 else []:
                tableColumnHeader.append(Paragraph('{heat}'.format(heat=h), styles['ColumnHeaderC']))
            tableColumnHeader.append(Paragraph('{time}'.format(time=config.displaySumTime), styles['ColumnHeaderC']))
        elif result['type'] == 'finale':
            headerRow += [None] * 2     # Add dummy cells
            subTableColumns = (12*mm, 68*mm, 24*mm, 12*mm, 12*mm, 22*mm)
            subTableColumnHeader = [
                Paragraph('{lane}'.format(lane=config.timetableHeaderLane), styles['ColumnHeaderC']),
                Paragraph('{team} / {company}'.format(team=config.timetableHeaderTeam, company=config.timetableHeaderCompany), styles['ColumnHeader']),
                Paragraph('{skipper}'.format(skipper=config.timesHeaderSkipper), styles['ColumnHeader']),
                Paragraph('{rank}'.format(rank=config.timesHeaderRank), styles['ColumnHeaderC']),
                Paragraph('{place}'.format(place=config.timesHeaderPlace), styles['ColumnHeaderC']),
                Paragraph('{time}'.format(time=config.timesHeaderTime), styles['ColumnHeaderC'])
            ]
            mainTableColumns = (15*mm, 15*mm, sum(subTableColumns))
            tableColumnHeader = [
                Paragraph('{time}'.format(time=config.timetableHeaderTime), styles['ColumnHeaderC']),
                Paragraph('{race}'.format(race=config.timetableHeaderName), styles['ColumnHeaderC']),
                Table([subTableColumnHeader], colWidths=subTableColumns, style=subTableHeaderStyle)
            ]
        elif result['type'] == 'rankingFinals':
            if config.raceToTopFinal:
                bestTimeTableColumns=(16*mm, 16*mm)
                mainTableColumns = (12*mm, 50*mm, 44*mm, sum(bestTimeTableColumns), 20*mm, 22*mm)
            else:
                mainTableColumns = (12*mm, 50*mm, 54*mm, 42*mm, 22*mm)

            # Add dummy cells to header based on column count
            headerRow += [None] * (len(mainTableColumns) - len(headerRow))

            tableColumnHeader = []
            tableColumnHeader.append(Paragraph('{rank}'.format(rank=config.timesHeaderRank), styles['ColumnHeaderC']))
            tableColumnHeader.append(Paragraph('{team}'.format(team=config.timetableHeaderTeam), styles['ColumnHeader']))
            tableColumnHeader.append(Paragraph('{company}'.format(company=config.timetableHeaderCompany), styles['ColumnHeader']))
            if config.raceToTopFinal:
                tableColumnHeader.append(
                    Table(
                        [
                            [
                                Paragraph('{bt}'.format(bt=config.displayBestTime), styles['ColumnHeaderC']),
                                None
                            ],
                            [
                                Paragraph('{btheats}'.format(btheats=config.heatsTitle), styles['ColumnHeaderC']),
                                Paragraph('{btfinals}'.format(btfinals=config.finaleTitle), styles['ColumnHeaderC'])
                            ]
                        ],
                        spaceBefore=0,
                        spaceAfter=0,
                        style=TableStyle([
                            ('BOTTOMPADDING',   (0, 0), (-1, -1), 0),
                            ('TOPPADDING',      (0, 0), (-1, -1), 0),
                            ('SPAN',            (0, 0), (-1,  0))
                        ]),
                        colWidths=bestTimeTableColumns
                    )
                )
                tableColumnHeader.append(Paragraph('{races}'.format(races=config.displayRaces), styles['ColumnHeaderC']))
            else:
                tableColumnHeader.append(Paragraph('{bt} {btheats}'.format(bt=config.displayBestTime, btheats=config.heatsTitle), styles['ColumnHeaderC']))
            tableColumnHeader.append(Paragraph('{time}'.format(time=config.displayFinalTime), styles['ColumnHeaderC']))
        else:
            skipResults = True

        tableData.append(headerRow)

        if not skipResults:
            # Heats and finale
            if 'races' in result and len(result['races']) > 0:
                tableData.append(tableColumnHeader)
                for race in result['races']:
                    raceRow = []
                    raceRow.append(
                        Paragraph('{time}'.format(time=race['time'].strftime('%H:%M')), styles['NormalC'])
                    )
                    raceRow.append(
                        Paragraph('{racename}'.format(racename=race['desc']), styles['NormalC'])
                    )

                    # Lanes as sub-table
                    laneTable = []
                    for lane in race['lanes']:
                        laneRow = []
                        laneRow.append(
                            Paragraph('{racelane}'.format(racelane=lane['lane']), styles['NormalC'])
                        )
                        if 'draw' in lane and lane['draw']:
                            laneRow.append(
                                Paragraph('{team}'.format(team=lane['team']), styles['NormalI'])
                            )
                        else:
                            laneRow.append(
                                [
                                    Paragraph('{team}'.format(team=lane['team']), styles['NormalB']),
                                    Paragraph('{company}'.format(company=lane['company']), styles['Secondary'])
                                ]
                            )
                        laneRow.append(
                            Paragraph('{skipper}'.format(skipper=lane['skipper']['name'] if 'name' in lane['skipper'] else '-'), styles['Normal'])
                        )
                        if result['type'] == 'finale':
                            hasRank = 'rank' in lane and lane['rank'] != '-'
                            laneRow.append(
                                Paragraph('{rank}'.format(rank=lane['rank'] if hasRank else '-'), styles['NormalBCLink'] if hasRank else styles['NormalC'])
                            )
                        laneRow.append(
                            Paragraph('{place}'.format(place=lane['place']), styles['NormalC'])
                        )
                        finished = lane['time'] is not None and lane['time'] > 0.0
                        laneRow.append(
                            Paragraph('{time}'.format(time=asTime(lane['time']) if finished else '-'), styles['NormalBC'] if finished else styles['NormalC'])
                        )
                        laneTable.append(laneRow)
                    raceRow.append(Table(laneTable, colWidths=subTableColumns, style=subTableStyle))

                    tableData.append(raceRow)

            # Ranking heats
            if result['type'] == 'rankingHeats' and 'ranks' in result and len(result['ranks']) > 0:
                tableData.append(tableColumnHeader)
                brackets = {}
                for team in result['ranks']:
                    rankRow = []
                    rankRow.append(Paragraph('{rank}'.format(rank=team['rank']), styles['NormalBCLink']))
                    rankRow.append(Paragraph('{name}'.format(name=team['name']), styles['NormalB']))
                    rankRow.append(Paragraph('{company}'.format(company=team['company']), styles['Secondary']))
                    for i, t in enumerate(team['times']):
                        if i > hc:
                            break
                        rankRow.append(Paragraph('{time}'.format(time=asTime(t) if t > 0 else '-'), styles['SecondaryC']))
                    rankRow.append(Paragraph('{time}'.format(time=asTime(sum(team['times']))), styles['NormalBC']))

                    if team['races'] not in brackets.keys():
                        brackets[team['races']] = []
                    brackets[team['races']].append(rankRow)

                # Split brackets apart
                for i, bracket in enumerate(brackets.keys()):
                    # Insert empty row to separate brackets
                    if i > 0:
                        tableData.append([None] * len(mainTableColumns))
                    # Insert rank bracket
                    for rankRow in brackets[bracket]:
                        tableData.append(rankRow)

            # Ranking Finale
            if result['type'] == 'rankingFinals' and 'ranks' in result and len(result['ranks']) > 0:
                tableData.append(tableColumnHeader)
                for team in result['ranks']:
                    rankRow = []
                    rankRow.append(Paragraph('{rank}'.format(rank=team['rank']), styles['NormalBCLink']))
                    rankRow.append(Paragraph('{team}'.format(team=team['team']), styles['NormalB']))
                    rankRow.append(Paragraph('{company}'.format(company=team['company']), styles['Secondary']))
                    if config.raceToTopFinal:
                        rankRow.append(
                            Table(
                                [
                                    [
                                        Paragraph('{bthtime}'.format(bthtime=asTime(team['bt_heats'])), styles['SecondaryC']),
                                        Paragraph('{btftime}'.format(btftime=asTime(team['bt_finale'])), styles['SecondaryC'])
                                    ]
                                ],
                                spaceBefore=0,
                                spaceAfter=0,
                                style=subTableHeaderStyle,
                                colWidths=bestTimeTableColumns
                            )
                        )
                        rankRow.append(Paragraph('{races}'.format(races=team['races']), styles['NormalC']))
                    else:
                        rankRow.append(Paragraph('{bthtime}'.format(bthtime=asTime(team['bt_heats'])), styles['NormalBC']))
                    rankRow.append(Paragraph('{ftime}'.format(ftime=asTime(team['finale_time'])), styles['NormalBC']))
                    tableData.append(rankRow)

        # Insert a page break after each section
        if result['type'] != 'heat':
            story.append(PageBreak())

        # Insert table into story
        story.append(
            LongTable(
                tableData,
                style=mainTableStyle,
                repeatRows=2,
                spaceBefore=5*mm,
                colWidths=mainTableColumns
            )
        )

    # Create a file-like buffer to receive PDF data
    pdf_buffer = io.BytesIO()

    # Create document
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        leftMargin=15*mm,
        rightMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=20*mm
    )
    doc.title = filename
    doc.creator = config.ownerName
    doc.author = config.ownerName
    doc.subject = config.siteName
    doc.keywords = [config.siteAbbr, config.timetableHeader]

    doc.build(story, canvasmaker=PageNumCanvas)

    pdf_buffer.seek(0)

    # FileResponse sets the Content-Disposition header (as_attachment=True)
    # so that browsers present the option to save the file
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)

def trainings(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated:
        return redirect('/')

    # Provide a filename for the PDF
    filename = '{at}_{abbr}_trainings.pdf'.format(
        at=datetime.now().strftime("%Y%m%d-%H%M%S"),
        abbr=config.siteAbbr
    )

    # Define styling
    styles = pdfStyleSheet()
    mainTableStyle = TableStyle([
        ('BOX',             (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # border for whole table
        ('LINEABOVE',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # top border for each row
        ('LINEBELOW',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # bottom border for each row
        ('LINEBELOW',       (0,  1), (-1,  1), 0.5 , colors.grey),                          # line under colum header row
        ('SPAN',            (0,  0), (-1,  0)),                                             # span title row (1st row)
        ('VALIGN',          (0,  2), ( 0, -1), 'MIDDLE'),                                   # id middle-aligned
        ('VALIGN',          (1,  2), (-1, -1), 'TOP'),                                      # everything else is top-aligned
        ('ROWBACKGROUNDS',  (0,  0), (-1, -1), (colors.whitesmoke, colors.transparent)),    # alternate row coloring
    ])
    statTableStyle = TableStyle([
        ('BOX',             (0,  0), (-1, -1), 0.25, colors.lightgrey),
        ('GRID',            (0,  0), (-1, -1), 0.25, colors.lightgrey),
        ('BOTTOMPADDING',   (0,  0), (-1, -1), 6),
        ('TOPPADDING',      (0,  0), (-1, -1), 6),
    ])

    # Gather data
    trainingsContent = getTrainingsContent()
    trainingsTableData = [
        {
            # Upcoming Trainings
            'header': Paragraph('{trainingsStatus}'.format(trainingsStatus=config.trainingsTitleUpcoming), styles['TableHeader']),
            'data': trainingsContent['trainingsList']['upcoming']
        },
        {
            # Past Trainings
            'header': Paragraph('{trainingsStatus}'.format(trainingsStatus=config.trainingsTitlePast), styles['TableHeader']),
            'data': trainingsContent['trainingsList']['past']
        },
        {
            # Inactive Trainings
            'header': Paragraph('{trainingsStatus}'.format(trainingsStatus=config.trainingsTitleInactive), styles['TableHeader']),
            'data': trainingsContent['trainingsList']['inactive']
        }
    ]

    # Start story with front page
    story = [
        Spacer(width=0, height=20*mm),
        Paragraph('{event}'.format(event=config.siteName), styles['Title']),
        Paragraph('{date}'.format(date=config.eventDate.strftime('%d. %B %Y')), styles['SubTitle']),
        Spacer(width=0, height=20*mm),
        Paragraph('{title}'.format(title=config.trainingsTrainings), styles['Title'])
    ]

    # Frontpage statistics section
    statTableData = [
        [
            Paragraph('{trainingsStatus}'.format(trainingsStatus=config.trainingsTitleTotal), styles['TableHeaderBLink']),
            Paragraph('{count}'.format(count=Training.objects.all().count()), styles['TableHeaderBCLink'])
        ]
    ]
    for trainingsTable in trainingsTableData:
        statTableData.append(
            [
                trainingsTable['header'],
                Paragraph('{count}'.format(count=len(trainingsTable['data'])), styles['TableHeaderBC']),
            ]
        )

    statTable = Table(
        statTableData,
        style=statTableStyle,
        colWidths=(130*mm, 50*mm)
    )
    story.append(
        TopPadder(
            Table(
                [
                    [statTable],
                    [Spacer(width=0, height=10*mm)]
                ]
            )
        )
    )
    story.append(PageBreak())

    # Layout trainings content
    tableColumnHeader = [
        Paragraph('{id}'.format(id=config.trainingsTableHeaderID), styles['ColumnHeaderC']),
        Paragraph('{date}'.format(date=config.placeholderTrainingDateTime), styles['ColumnHeader']),
        Paragraph('{team} / {company}'.format(team=config.teamTableHeaderTeam, company=config.teamTableHeaderCompany), styles['ColumnHeader']),
        Paragraph('{contact}'.format(contact=config.placeholderTeamCaptain), styles['ColumnHeader']),
        Paragraph('{skipper}'.format(skipper=config.skipper), styles['ColumnHeader']),
        Paragraph('{note}'.format(note=config.placeholderTrainingNotes), styles['ColumnHeader'])
    ]
    tableColumnWidth=(10*mm, 25*mm, 35*mm, 45*mm, 45*mm, 20*mm)
    for trainingsTable in trainingsTableData:
        if len(trainingsTable['data']) <= 0:
                continue
        tableData = [
            [
                trainingsTable['header']
            ],
            tableColumnHeader
        ]
        for n, training in enumerate(trainingsTable['data']):
            trainingRow = []
            trainingRow.append(
                Paragraph('{id}'.format(id=(n + 1)), styles['NormalC'])
            )
            trainingRow.append(
                [
                    Paragraph('{date}'.format(date=training['date'].strftime('%d.%m.%Y')), styles['NormalB']),
                    Paragraph('{start} - {end}'.format(start=training['time_start'].strftime('%H:%M'), end=training['time_end'].strftime('%H:%M')), styles['Secondary'])
                ]
            )
            trainingRow.append(
                [
                    Paragraph('{name}'.format(name=training['team']['name']), styles['NormalB']),
                    Paragraph('{company}'.format(company=training['team']['company']), styles['Secondary'])
                ]
            )
            trainingRow.append(
                [
                    Paragraph('{contact}'.format(contact=training['team']['contact']), styles['NormalB']),
                    Paragraph('<a href="mailto:{email}">{email}</a>'.format(email=training['team']['email']), styles['SecondaryLink']),
                    Paragraph('{phone}'.format(phone=training['team']['phone']), styles['Secondary'])
                ]
            )
            trainingRow.append(
                [
                    Paragraph('{skipper}'.format(skipper=training['skipper']['name'] if training['skipper']['name'] is not None else ''), styles['Normal']),
                    Paragraph('<a href="mailto:{email}">{email}</a>'.format(email=training['skipper']['email'] if training['skipper']['name'] is not None else ''), styles['SecondaryLink'])
                ]
            )
            trainingRow.append(
                Paragraph('{note}'.format(note=training['notes'] if training['notes'] is not None else ''), styles['Secondary'])
            )
            tableData.append(trainingRow)

        story.append(
            LongTable(
                tableData,
                style=mainTableStyle,
                repeatRows=2,
                colWidths=tableColumnWidth
            )
        )
        story.append(Spacer(width=0, height=10*mm))

    story.append(PageBreak())

    # Trainings statstics
    tableColumnWidth=(10*mm, 10*mm, 50*mm, 110*mm)
    mainTableStyle.add('VALIGN', (0, 2), (-1, -1), 'MIDDLE')
    for statisticsData in trainingsContent['trainingsStats']:
        if statisticsData['maxTrainings'] <= 0:
            continue
        tableColumnHeader = [
            Paragraph('{id}'.format(id=statisticsData['table_header']['id']), styles['ColumnHeaderC']),
            Paragraph('{total}'.format(total=statisticsData['table_header']['total']), styles['ColumnHeader']),
            Paragraph('{name}'.format(name=statisticsData['table_header']['name']), styles['ColumnHeader']),
            Paragraph('{stat}'.format(stat=statisticsData['table_header']['stat']), styles['ColumnHeader'])
        ]
        tableData = [
            [
                Paragraph('{header}'.format(header=statisticsData['header']), styles['TableHeader'])
            ],
            tableColumnHeader
        ]
        for n, statData in enumerate(statisticsData['stats']):
            trainingRow = []
            trainingRow.append(
                Paragraph('{id}'.format(id=(n + 1)), styles['NormalC'])
            )
            trainingRow.append(
                Paragraph('{total}'.format(total=statData['totalTrainings']), styles['Normal']),
            )
            trainingRow.append(
                [
                    Paragraph('{name}'.format(name=statData['name']), styles['NormalB']),
                    Paragraph(
                        '<a href="mailto:{email}">{email}</a>'.format(email=statData['subname']), styles['SecondaryLink']
                    ) if statisticsData['type'] == 'skipper' else Paragraph(
                        '{subname}'.format(subname=statData['subname']), styles['Secondary']
                    )
                ]
            )

            statColWidths = []
            statTableStyle = TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROUNDEDCORNERS', [3, 3, 3, 3]),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0)
            ])
            statColData = []
            col = 0
            if statData['upcomingTrainings'] > 0:
                statColWidths.append(max(12, ((105 / statisticsData['maxTrainings']) * statData['upcomingTrainings']))*mm)
                statColData.append(Paragraph('{stat}'.format(stat=statData['upcomingTrainings']), styles['MarkerBRSmallWhite']))
                statTableStyle.add('BACKGROUND', (col, 0), (col, -1), colors.HexColor('#f4c539'))
                col += 1
            if statData['pastTrainings'] > 0:
                statColWidths.append(max(12, ((105 / statisticsData['maxTrainings']) * statData['pastTrainings']))*mm)
                statColData.append(Paragraph('{stat}'.format(stat=statData['pastTrainings']), styles['MarkerBRSmallWhite']))
                statTableStyle.add('BACKGROUND', (col, 0), (col, -1), colors.HexColor('#418457'))
                col += 1
            if statData['inactiveTrainings'] > 0:
                statColWidths.append(max(12, ((105 / statisticsData['maxTrainings']) * statData['inactiveTrainings']))*mm)
                statColData.append(Paragraph('{stat}'.format(stat=statData['inactiveTrainings']), styles['MarkerBRSmallWhite']))
                statTableStyle.add('BACKGROUND', (col, 0), (col, -1), colors.HexColor('#6e757c'))
                col += 1

            trainingRow.append(Table([statColData], style=statTableStyle, colWidths=statColWidths))
            tableData.append(trainingRow)

        story.append(
            LongTable(
                tableData,
                style=mainTableStyle,
                repeatRows=2,
                colWidths=tableColumnWidth
            )
        )
        story.append(Spacer(width=0, height=10*mm))


    # Create a file-like buffer to receive PDF data
    pdf_buffer = io.BytesIO()

    # Create document
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        leftMargin=15*mm,
        rightMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=20*mm
    )
    doc.title = filename
    doc.creator = config.ownerName
    doc.author = config.ownerName
    doc.subject = config.siteName
    doc.keywords = [config.siteAbbr, config.trainingsTableHeader]

    doc.build(story, canvasmaker=PageNumCanvas)

    pdf_buffer.seek(0)

    # FileResponse sets the Content-Disposition header (as_attachment=True)
    # so that browsers present the option to save the file
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)

def billing(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated:
        return redirect('/')

    # Provide a filename for the PDF
    filename = '{at}_{abbr}_billing.pdf'.format(
        at=datetime.now().strftime("%Y%m%d-%H%M%S"),
        abbr=config.siteAbbr
    )

    # Define styling
    styles = pdfStyleSheet()
    tableStyle = TableStyle([
        ('BOX',             (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # border for whole table
        ('LINEABOVE',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # top border for each row
        ('LINEBELOW',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # bottom border for each row
        ('LINEBELOW',       (0,  1), (-1,  1), 0.5 , colors.grey),                          # line under colum header row
        ('SPAN',            (0,  0), (-1,  0)),                                             # span title row (1st row)
        ('VALIGN',          (0,  2), ( 0, -1), 'MIDDLE'),                                   # id middle-aligned
        ('VALIGN',          (1,  2), (-1, -1), 'TOP'),                                      # everything else is top-aligned
        ('ROWBACKGROUNDS',  (0,  0), (-1, -1), (colors.whitesmoke, colors.transparent)),    # alternate row coloring
        ('LINEABOVE',       (0, -1), (-1, -1), 0.5, colors.grey),                           # thicker line above summation row
        ('BACKGROUND',      (0, -1), (-1, -1), colors.white),                               # special background for summation row
        ('BOTTOMPADDING',   (0,  0), (-1,  0), 0),
        ('TOPPADDING',      (0,  0), (-1,  0), 0),
        ('LEFTPADDING',     (0,  0), (-1,  0), 0),
        ('RIGHTPADDING',    (0,  0), (-1,  0), 0)
    ])
    tableColumnWidth=(10*mm, 25*mm, 60*mm, 60*mm, 25*mm)
    headerTableStyle = TableStyle([
        ('VALIGN',          (0,  0), (-1,  0), 'MIDDLE')                                    # header row middle-aligned
    ])
    headerColumnWidth=(130*mm, 50*mm)

    # Start story with front page
    story = [
        Spacer(width=0, height=20*mm),
        Paragraph('{event}'.format(event=config.siteName), styles['Title']),
        Paragraph('{date}'.format(date=config.eventDate.strftime('%d. %B %Y')), styles['SubTitle']),
        Spacer(width=0, height=20*mm),
        Paragraph('{title}'.format(title=config.billingTitle), styles['Title'])
    ]

    story.append(PageBreak())

    # Individual skipper trainings
    availableSkippers = Skipper.objects.all()
    tableColumnHeaderSkipper = [
        Paragraph('{id}'.format(id=config.trainingsTableHeaderID), styles['ColumnHeaderC']),
        Paragraph('{date}'.format(date=config.placeholderTrainingDateTime), styles['ColumnHeader']),
        Paragraph('{team} / {company}'.format(team=config.teamTableHeaderTeam, company=config.teamTableHeaderCompany), styles['ColumnHeader']),
        Paragraph('{note}'.format(note=config.placeholderTrainingNotes), styles['ColumnHeader']),
        Paragraph('{compensation}'.format(compensation=config.headerCompensation), styles['ColumnHeaderR'])
    ]

    for skipper in availableSkippers:
        skipperTrainings = []
        try:
            skipperTrainings = Training.objects.filter(skipper_id=skipper.id)
        except:
            continue

        if len(skipperTrainings) <= 0:
            continue

        tableData = [
            [
                Table(
                    [
                        [
                            [
                                Paragraph('{fname} {lname}'.format(fname=skipper.fname, lname=skipper.lname), styles['TableHeader']),
                                Paragraph('<a href="mailto:{email}">{email}</a>'.format(email=skipper.email), styles['SecondaryLink'])
                            ],
                            Paragraph('{type}'.format(type=config.skipperTag), styles['MarkerBRLink'])
                        ]
                    ],
                    style=headerTableStyle,
                    colWidths=headerColumnWidth
                )
            ],
            tableColumnHeaderSkipper
        ]
        for n, training in enumerate(skipperTrainings):
            team = None
            try:
                team = Team.objects.get(id=training.team_id)
            except:
                pass

            trainingRow = []
            trainingRow.append(
                Paragraph('{id}'.format(id=(n + 1)), styles['NormalC'])
            )
            trainingRow.append(
                [
                    Paragraph('{date}'.format(date=training.date.strftime('%d.%m.%Y')), styles['NormalB']),
                    Paragraph(
                        '{start} - {end}'.format(
                            start=training.time.strftime('%H:%M'),
                            end=(datetime.combine(date.today(), training.time) + training.duration).time().strftime('%H:%M')
                        ),
                        styles['Secondary']
                    )
                ]
            )
            trainingRow.append(
                [
                    Paragraph('{team}'.format(team=team.name), styles['NormalB']),
                    Paragraph('{company}'.format(company=team.company), styles['Secondary'])
                ]
            )
            trainingRow.append(
                Paragraph('{note}'.format(note=training.notes if training.notes is not None else ''), styles['Secondary'])
            )
            trainingRow.append(
                Paragraph(
                    '{compensation} {currency}'.format(
                        compensation=config.skipperTrainingsCompensation,
                        currency=config.currency
                    ),
                    styles['NormalR']
                )
            )
            tableData.append(trainingRow)

        # Sum of compensations
        tableData.append(
            [
                Paragraph('{sum}'.format(sum=config.trainingsCountTrainings), styles['NormalBC']),
                Paragraph('{count}'.format(count=len(skipperTrainings)), styles['NormalBR']),
                Paragraph('{text}'.format(text=config.trainingsTrainings), styles['NormalB']),
                Paragraph('{text}'.format(text=config.sumFees), styles['NormalBR']),
                Paragraph(
                    '{compensation} {currency}'.format(
                        compensation=config.skipperTrainingsCompensation * len(skipperTrainings),
                        currency=config.currency
                    ),
                    styles['NormalBR']
                )
            ]
        )

        story.append(
            LongTable(
                tableData,
                style=tableStyle,
                repeatRows=2,
                colWidths=tableColumnWidth
            )
        )
        story.append(PageBreak())

    # Individual team trainings
    availableTeams = Team.objects.all()
    tableColumnHeaderTeam = [
        Paragraph('{id}'.format(id=config.trainingsTableHeaderID), styles['ColumnHeaderC']),
        Paragraph('{date}'.format(date=config.placeholderTrainingDateTime), styles['ColumnHeader']),
        Paragraph('{skipper}'.format(skipper=config.skipper), styles['ColumnHeader']),
        Paragraph('{note}'.format(note=config.placeholderTrainingNotes), styles['ColumnHeader']),
        Paragraph('{fee}'.format(fee=config.headerFee), styles['ColumnHeaderR'])
    ]

    for team in availableTeams:
        teamTrainings = []
        try:
            teamTrainings = Training.objects.filter(team_id=team.id)
        except:
            pass

        if len(teamTrainings) <= 0 and (not team.active or team.wait):
            continue

        tableData = [
            [
                Table(
                    [
                        [
                            [
                                Paragraph('{team}'.format(team=team.name), styles['TableHeader']),
                                Paragraph('{company}'.format(company=team.company), styles['Normal']),
                            ],
                            Paragraph('{type}'.format(type=config.teamTag), styles['MarkerBRLink'])
                        ]
                    ],
                    style=headerTableStyle,
                    colWidths=headerColumnWidth
                )
            ],
            tableColumnHeaderTeam
        ]
        for n, training in enumerate(teamTrainings):
            skipper = None
            try:
                skipper = Skipper.objects.get(id=training.skipper_id)
            except:
                pass

            trainingRow = []
            trainingRow.append(
                Paragraph('{id}'.format(id=(n + 1)), styles['NormalC'])
            )
            trainingRow.append(
                [
                    Paragraph('{date}'.format(date=training.date.strftime('%d.%m.%Y')), styles['NormalB']),
                    Paragraph(
                        '{start} - {end}'.format(
                            start=training.time.strftime('%H:%M'),
                            end=(datetime.combine(date.today(), training.time) + training.duration).time().strftime('%H:%M')
                        ),
                        styles['Secondary']
                    )
                ]
            )
            trainingRow.append(
                [
                    Paragraph('{skipper}'.format(skipper=skipper.name), styles['Normal']),
                    Paragraph('<a href="mailto:{email}">{email}</a>'.format(email=skipper.email), styles['SecondaryLink'])
                ] if skipper is not None else Paragraph('')
            )
            trainingRow.append(
                Paragraph('{note}'.format(note=training.notes if training.notes is not None else ''), styles['Secondary'])
            )
            trainingRow.append(
                Paragraph(
                    '{fee} {currency}'.format(
                        fee=0 if config.firstTrainingIsFree and n == 0 and team.active and not team.wait else config.trainingsFee,
                        currency=config.currency
                    ),
                    styles['NormalR']
                )
            )
            tableData.append(trainingRow)

        # Add event fee
        fees = 0
        if team.active and not team.wait:
            tableData.append(
                [
                    Paragraph('{tag}'.format(tag=config.racedayTag), styles['NormalBC']),
                    Paragraph('{date}'.format(date=config.eventDate.strftime('%d.%m.%Y')), styles['NormalB']),
                    Paragraph('{event}'.format(event=config.siteName), styles['NormalBC']),
                    None,
                    Paragraph(
                        '{fee} {currency}'.format(
                            fee=0 if team.nofee else config.eventFee,
                            currency=config.currency
                        ),
                        styles['NormalBR']
                    )
                ]
            )
            tableStyle.add('SPAN', (2, -2), (3, -2))

            # Team has to pay the event fee only if it is not exempted (sponsor)
            if not team.nofee:
                fees += config.eventFee

        # Sum of fees
        fees += config.trainingsFee * len(teamTrainings)                                                # add each training
        if config.firstTrainingIsFree and team.active and not team.wait and len(teamTrainings) > 0:     # first training is free? (only for active teams)
            fees -= config.trainingsFee
        tableData.append(
            [
                Paragraph('{sum}'.format(sum=config.trainingsCountTrainings), styles['NormalBC']),
                Paragraph('{count}'.format(count=len(teamTrainings)), styles['NormalBR']),
                Paragraph('{text}'.format(text=config.trainingsTrainings), styles['NormalB']),
                Paragraph('{text}'.format(text=config.sumFees), styles['NormalBR']),
                Paragraph('{fee} {currency}'.format(fee=fees, currency=config.currency), styles['NormalBR'])
            ]
        )

        story.append(
            LongTable(
                tableData,
                style=tableStyle,
                repeatRows=2,
                colWidths=tableColumnWidth
            )
        )
        story.append(PageBreak())

    # Create a file-like buffer to receive PDF data
    pdf_buffer = io.BytesIO()

    # Create document
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        leftMargin=15*mm,
        rightMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=20*mm
    )
    doc.title = filename
    doc.creator = config.ownerName
    doc.author = config.ownerName
    doc.subject = config.siteName
    doc.keywords = [config.siteAbbr, config.billingTitle]

    doc.build(story, canvasmaker=PageNumCanvas)

    pdf_buffer.seek(0)

    # FileResponse sets the Content-Disposition header (as_attachment=True)
    # so that browsers present the option to save the file
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)

def skippers(request):
    # handle login/logout
    loginUser(request)

    if not request.user.is_authenticated:
        return redirect('/')

    # Provide a filename for the PDF
    filename = '{at}_{abbr}_skippers.pdf'.format(
        at=datetime.now().strftime("%Y%m%d-%H%M%S"),
        abbr=config.siteAbbr
    )

    # Define styling
    styles = pdfStyleSheet()
    mainTableStyle = TableStyle([
        ('BOX',             (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # border for whole table
        ('LINEABOVE',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # top border for each row
        ('LINEBELOW',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                     # bottom border for each row
        ('LINEBELOW',       (0,  1), (-1,  1), 0.5 , colors.grey),                          # line under colum header row
        ('SPAN',            (0,  0), (-1,  0)),                                             # span title row (1st row)
        ('VALIGN',          (0,  2), (-1, -1), 'MIDDLE'),                                   # columns middle-aligned
        ('ROWBACKGROUNDS',  (0,  0), (-1, -1), (colors.whitesmoke, colors.transparent)),    # alternate row coloring
    ])
    statTableStyle = TableStyle([
        ('BOX',             (0,  0), (-1, -1), 0.25, colors.lightgrey),
        ('GRID',            (0,  0), (-1, -1), 0.25, colors.lightgrey),
        ('BOTTOMPADDING',   (0,  0), (-1, -1), 6),
        ('TOPPADDING',      (0,  0), (-1, -1), 6),
    ])

    # Gather data
    skipperTableData = [
        {
            # Active Skippers
            'header': Paragraph('{skipperListHeader} {skipperStatus}'.format(skipperListHeader=config.skippersTitle, skipperStatus=config.activeSkipperTitle), styles['TableHeader']),
            'data': Skipper.objects.filter(active=True).order_by(F('name').asc(nulls_last=True))
        },
        {
            # Inactive Skippers
            'header': Paragraph('{skipperListHeader} {skipperStatus}'.format(skipperListHeader=config.skippersTitle, skipperStatus=config.inactiveSkipperTitle), styles['TableHeader']),
            'data': Skipper.objects.filter(active=False).order_by(F('name').asc(nulls_last=True))
        }
    ]

    # Table column header is the same for all tables
    tableColumnHeader = [
        Paragraph('{id}'.format(id=config.skipperTableHeaderID), styles['ColumnHeaderC']),
        Paragraph('{name}'.format(name=config.placeholderSkipperName), styles['ColumnHeader']),
        Paragraph('{fname}'.format(fname=config.placeholderSkipperFName), styles['ColumnHeader']),
        Paragraph('{lname}'.format(lname=config.placeholderSkipperLName), styles['ColumnHeader']),
        Paragraph('{email}'.format(email=config.placeholderSkipperEmail), styles['ColumnHeader'])
    ]

    # Start story with front page
    story = [
        Spacer(width=0, height=20*mm),
        Paragraph('{event}'.format(event=config.siteName), styles['Title']),
        Paragraph('{date}'.format(date=config.eventDate.strftime('%d. %B %Y')), styles['SubTitle']),
        Spacer(width=0, height=20*mm),
        Paragraph('{skipperList}'.format(skipperList=config.skippersListHeading), styles['Title'])
    ]

    # Statistics section
    statTableData = []
    for skipperTable in skipperTableData:
        statTableData.append(
            [
                skipperTable['header'],
                Paragraph('{count}'.format(count=len(skipperTable['data'])), styles['TableHeaderBC']),
            ]
        )

    statTable = Table(
        statTableData,
        style=statTableStyle,
        colWidths=(130*mm, 50*mm)
    )
    story.append(
        TopPadder(
            Table(
                [
                    [statTable],
                    [Spacer(width=0, height=10*mm)]
                ]
            )
        )
    )
    story.append(PageBreak())

    # Main Tables
    for skipperTable in skipperTableData:
        tableData = [
            [
                skipperTable['header']
            ],
            tableColumnHeader
        ]
        for i, skipper in enumerate(skipperTable['data']):
            skipperRow = []
            skipperRow.append(
                Paragraph('{id}'.format(id=(i + 1)), styles['NormalC'])
            )
            skipperRow.append(
                Paragraph('{name}'.format(name=skipper.name), styles['NormalB'])
            )
            skipperRow.append(
                Paragraph('{fname}'.format(fname=skipper.fname), styles['Normal'])
            )
            skipperRow.append(
                Paragraph('{lname}'.format(lname=skipper.lname), styles['Normal'])
            )
            skipperRow.append(
                Paragraph('<a href="mailto:{email}">{email}</a>'.format(email=skipper.email), styles['NormalLink'])
            )
            tableData.append(skipperRow)

        story.append(
            LongTable(
                tableData,
                style=mainTableStyle,
                repeatRows=2,
                colWidths=(10*mm, 32*mm, 32*mm, 32*mm, 74*mm)
            )
        )

        # Insert a spacer between new tables
        story.append(Spacer(width=0, height=10*mm))

    # Create a file-like buffer to receive PDF data
    pdf_buffer = io.BytesIO()

    # Create document
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        leftMargin=15*mm,
        rightMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=20*mm
    )
    doc.title = filename
    doc.creator = config.ownerName
    doc.author = config.ownerName
    doc.subject = config.siteName
    doc.keywords = [config.siteAbbr, config.skippersTitle]

    doc.build(story, canvasmaker=PageNumCanvas)

    pdf_buffer.seek(0)

    # FileResponse sets the Content-Disposition header (as_attachment=True)
    # so that browsers present the option to save the file
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)