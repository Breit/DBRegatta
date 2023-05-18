import io
from constance import config
from datetime import datetime

from django.http import FileResponse
from django.shortcuts import redirect
from django.db.models import F

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, LongTable, TableStyle, PageBreak, Spacer, TopPadder

from .views_helper import loginUser, getTimeTableContent
from .pdf_helper import *
from .models import Team, Post

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
        ('BOX',             (0,  0), (-1, -1), 0.25, colors.lightgrey),                             # border for whole table
        ('LINEABOVE',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                             # top border for each row
        ('LINEBELOW',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                             # bottom border for each row
        ('LINEBELOW',       (0,  1), (-1,  1), 0.5 , colors.grey),                                  # line under colum header row
        ('SPAN',            (0,  0), (-1,  0)),                                                     # span title row (1st row)
        ('SPAN',            (4,  1), ( 5,  1)),                                                     # span signup columns
        ('VALIGN',          (0,  2), ( 0, -1), 'MIDDLE'),                                           # id middle-aligned
        ('VALIGN',          (1,  2), ( 3, -1), 'TOP'),                                              # team, contact and address top-aligned
        ('VALIGN',          (4,  2), ( 5, -1), 'MIDDLE'),                                           # signup centered
        ('ROWBACKGROUNDS',  (0,  0), (-1, -1), (colors.HexColor('#f1f1f2'), colors.transparent)),   # alternate row coloring
    ])
    statTableStyle = TableStyle([
        ('BOX',             (0,  0), (-1, -1), 0.25, colors.lightgrey),
        ('GRID',            (0,  0), (-1, -1), 0.25, colors.lightgrey),
        ('BOTTOMPADDING',   (0,  0), (-1, -1), 6),
        ('TOPPADDING',      (0,  0), (-1, -1), 6),
    ])

    # Gather data
    teamTableData = [
        {
            # Active Teams
            'header': Paragraph('{teamListHeader} {teamStatus}'.format(teamListHeader=config.teamTableHeaderTeams, teamStatus=config.activeTeams), styles['TableHeader']),
            'data': Team.objects.filter(active=True, wait=False).order_by(F('position').asc(nulls_last=True))
        },
        {
            # Waitlist Teams
            'header': Paragraph('{teamListHeader} {teamStatus}'.format(teamListHeader=config.teamTableHeaderTeams, teamStatus=config.waitlistTeams), styles['TableHeader']),
            'data': Team.objects.filter(active=True, wait=True).order_by(F('position').asc(nulls_last=True))
        },
        {
            # Inactive Teams
            'header': Paragraph('{teamListHeader} {teamStatus}'.format(teamListHeader=config.teamTableHeaderTeams, teamStatus=config.inactiveTeams), styles['TableHeader']),
            'data': Team.objects.filter(active=False).order_by(F('position').asc(nulls_last=True))
        }
    ]

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
    for teamTable in teamTableData:
        statTableData.append(
            [
            teamTable['header'],
            Paragraph('<b>{count}</b>'.format(count=len(teamTable['data'])), styles['TableHeaderC']),
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

    # Get team content: active teams
    for i, teamTable in enumerate(teamTableData):
        tableData = [
            [
                teamTable['header']
            ],
            tableColumnHeader
        ]
        for team in teamTable['data']:
            teamRow = []
            teamRow.append(
                Paragraph('{id}'.format(id=team.id), styles['NormalC'])
            )
            teamRow.append(
                [
                    Paragraph('<b>{name}</b>'.format(name=team.name), styles['Normal']),
                    Paragraph('{company}'.format(company=team.company), styles['Secondary'])
                ]
            )
            teamRow.append(
                [
                    Paragraph('<b>{contact}</b>'.format(contact=team.contact), styles['Normal']),
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

        # Insert a page break for new tables
        if i > 0:
            story.append(PageBreak())

        story.append(
            LongTable(
                tableData,
                style=mainTableStyle,
                repeatRows=2,
                colWidths=(10*mm, 50*mm, 50*mm, 38*mm, 10*mm, 22*mm)
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
    doc.keywords = [config.siteAbbr, config.teamListHeader]

    doc.build(story, canvasmaker=PageNumCanvas)

    pdf_buffer.seek(0)

    # FileResponse sets the Content-Disposition header (as_attachment=True)
    # so that browsers present the option to save the file
    return FileResponse(pdf_buffer, as_attachment=False, filename=filename)

def timetable(request):
    # handle login/logout
    loginUser(request)

    # Provide a filename for the PDF
    filename = '{at}_{abbr}_timetable.pdf'.format(
        at=datetime.now().strftime("%Y%m%d-%H%M%S"),
        abbr=config.siteAbbr
    )

    # Define styling
    styles = pdfStyleSheet()
    mainTableStyle = TableStyle([
        ('BOX',             (0,  0), (-1, -1), 0.25, colors.lightgrey),                             # border for whole table
        ('SPAN',            (1,  0), (-1,  0)),                                                     # span table headers
        ('LINEABOVE',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                             # top border for each row
        ('LINEBELOW',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                             # bottom border for each row
        ('VALIGN',          (0,  0), (-1, -1), 'MIDDLE'),                                           # all cells middle-aligned
        ('ROWBACKGROUNDS',  (0,  0), (-1, -1), (colors.HexColor('#f1f1f2'), colors.transparent)),   # alternate row coloring
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
    subTableColumns = (12*mm, 50*mm, 62*mm, 23*mm)
    mainTableColumns = (18*mm, 15*mm, sum(subTableColumns))

    # Gather data
    timetableData = getTimeTableContent()

    # Table column header is the same for all tables
    subTableColumnHeader = [
        Paragraph('{lane}'.format(lane=config.timetableHeaderLane), styles['ColumnHeaderC']),
        Paragraph('{team}'.format(team=config.timetableHeaderTeam), styles['ColumnHeader']),
        Paragraph('{company}'.format(company=config.timetableHeaderCompany), styles['ColumnHeader']),
        Paragraph('{skipper}'.format(skipper=config.timetableHeaderSkipper), styles['ColumnHeader'])
    ]
    tableColumnHeader = [
        Paragraph('{time}'.format(time=config.timetableHeaderTime), styles['ColumnHeaderC']),
        Paragraph('{race}'.format(race=config.timetableHeaderName), styles['ColumnHeaderC']),
        Table([subTableColumnHeader], colWidths=subTableColumns, style=subTableHeaderStyle)
    ]

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
                    postFrameData
                )
            )
        )
    story.append(PageBreak())

    # Get team content: active teams
    for event in timetableData:
        tableData = []
        tableData.append(
            [
                Paragraph('<b>{time}</b>'.format(time=event['time'].strftime('%H:%M')), styles['TableHeaderC']),
                Paragraph('{agendum}'.format(agendum=event['desc']), styles['TableHeader']),
                None          # Dummies to fill the columns
            ]
        )
        if 'races' in event and len(event['races']) > 0:
            tableData.append(tableColumnHeader)
            for race in event['races']:
                raceRow = []
                raceRow.append(
                    Paragraph('<b>{time}</b>'.format(time=race['time'].strftime('%H:%M')), styles['NormalC'])
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
                            Paragraph('<i>{team}</i>'.format(team=lane['team']), styles['Normal'])
                        )
                    else:
                        laneRow.append(
                            Paragraph('<b>{team}</b>'.format(team=lane['team']), styles['Normal'])
                        )
                    laneRow.append(
                        Paragraph('{company}'.format(company=lane['company']), styles['Normal'])
                    )
                    laneRow.append(
                        Paragraph('{skipper}'.format(skipper=lane['skipper']['name'] if 'name' in lane['skipper'] else '-'), styles['Normal'])
                    )
                    laneTable.append(laneRow)
                raceRow.append(Table(laneTable, colWidths=subTableColumns, style=subTableStyle))

                tableData.append(raceRow)

        story.append(
            LongTable(
                tableData,
                style=mainTableStyle,
                repeatRows=2,
                spaceBefore=5*mm,
                colWidths=mainTableColumns
            )
        )

        # Insert a page break after each heat
        if 'type' in event and event['type'] == 'heat':
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
    doc.keywords = [config.siteAbbr, config.timetableHeader]

    doc.build(story, canvasmaker=PageNumCanvas)

    pdf_buffer.seek(0)

    # FileResponse sets the Content-Disposition header (as_attachment=True)
    # so that browsers present the option to save the file
    return FileResponse(pdf_buffer, as_attachment=False, filename=filename)
