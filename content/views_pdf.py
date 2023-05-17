import io
from constance import config
from datetime import datetime

from django.http import FileResponse
from django.shortcuts import redirect
from django.db.models import F

from reportlab.platypus import SimpleDocTemplate, Paragraph, LongTable, TableStyle, PageBreak

from .views_helper import loginUser
from .pdf_helper import *
from .models import Team

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
    tableStyle = TableStyle([
        ('BOX',             (0,  0), (-1, -1), 0.25, colors.lightgrey),                             # border for whole table
        ('LINEABOVE',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                             # top border for each row
        ('LINEBELOW',       (0,  0), (-1, -1), 0.25, colors.lightgrey),                             # bottom border for each row
        ('SPAN',            (4,  0), ( 5,  0)),                                                     # span signup columns
        ('LINEBELOW',       (0,  0), (-1,  0), 0.5 , colors.grey),                                  # line under colum header row
        ('VALIGN',          (0,  1), ( 0, -1), 'MIDDLE'),                                           # id middle-aligned
        ('VALIGN',          (1,  1), ( 3, -1), 'TOP'),                                              # team, contact and address top-aligned
        ('VALIGN',          (4,  1), ( 5, -1), 'MIDDLE'),                                           # signup centered
        ('ROWBACKGROUNDS',  (0,  0), (-1, -1), (colors.transparent, colors.HexColor('#f1f1f2'))),   # alternate row coloring
    ])

    # Gather data
    teamTableData = [
        {
            # Active Teams
            'header': Paragraph('{teamListHeader} {teamStatus}'.format(teamListHeader=config.teamTableHeaderTeams, teamStatus=config.activeTeams), styles['Heading1']),
            'data': Team.objects.filter(active=True, wait=False).order_by(F('position').asc(nulls_last=True))
        },
        {
            # Waitlist Teams
            'header': Paragraph('{teamListHeader} {teamStatus}'.format(teamListHeader=config.teamTableHeaderTeams, teamStatus=config.waitlistTeams), styles['Heading1']),
            'data': Team.objects.filter(active=True, wait=True).order_by(F('position').asc(nulls_last=True))
        },
        {
            # Inactive Teams
            'header': Paragraph('{teamListHeader} {teamStatus}'.format(teamListHeader=config.teamTableHeaderTeams, teamStatus=config.inactiveTeams), styles['Heading1']),
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

    # Start story
    story = []

    # Page header
    story.append(Paragraph('{teamList}'.format(teamList=config.teamListHeader), styles['Title']))

    # Get team content: active teams
    for i, teamTable in enumerate(teamTableData):
        tableData = [tableColumnHeader]
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

        story.append(teamTable['header'])
        story.append(
            LongTable(
                tableData,
                style=tableStyle,
                repeatRows=1,
                colWidths=(10*mm, 40*mm, 50*mm, 48*mm, 10*mm, 22*mm)
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
