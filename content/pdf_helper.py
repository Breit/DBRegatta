"""
Helper functions and classes for PDF file rendering

All in here is fixed to A4 page size and the purpose of rendering
pages for the DBRegatta site and not necessarily universally usable
"""

import os
import re

from constance import config
from django.conf import settings

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.fonts import tt2ps, addMapping
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import StyleSheet1, ParagraphStyle

from reportlab.platypus import Paragraph, SimpleDocTemplate, Flowable

class PageNumCanvas(canvas.Canvas):
    """
    Derived canvas class to keep track of page numbers
    """
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        """
        On a page break, add information to the list
        """
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """
        Add the page number to each page (page x of y)
        """
        page_count = len(self.pages)

        for page in self.pages:
            self.__dict__.update(page)
            self.draw_header()
            self.draw_footer_page_number(page_count)
            self.draw_footer_logos()
            canvas.Canvas.showPage(self)

        canvas.Canvas.save(self)

    def draw_header(self):
        """
        Add event and date to the header
        """
        if self._pageNumber > 1:
            event = "{event}".format(event=config.siteName)
            date = "{date}".format(date=config.eventDate.strftime('%d. %B %Y'))
            self.setFont("Helvetica", 10)
            self.drawString(15*mm, A4[1] - 8*mm, event)
            self.drawRightString(A4[0] - 15*mm, A4[1] - 8*mm, date)

    def draw_footer_page_number(self, page_count):
        """
        Add the page number to the footer
        """
        page = "{page} / {pages}".format(page=self._pageNumber, pages=page_count)
        self.setFont("Helvetica", 8)
        self.drawCentredString(A4[0] / 2.0, 10*mm, page)

    def draw_footer_logos(self):
        """
        Add logos to the footer
        """
        sponsor_image = os.path.join(settings.MEDIA_ROOT, 'images', config.sponsorLogoReport)
        if os.path.isfile(sponsor_image):
            img = ImageReader(sponsor_image)
            iw, ih = img.getSize()
            aspect = iw / float(ih)
            height = 10*mm
            width = height * aspect
            self.drawImage(img, 15*mm, 8*mm, width=width, height=height, mask='auto')

        owner_image = os.path.join(settings.MEDIA_ROOT, 'images', config.ownerLogoReport)
        if os.path.isfile(owner_image):
            img = ImageReader(owner_image)
            iw, ih = img.getSize()
            aspect = iw / float(ih)
            height = 10*mm
            width = height * aspect
            self.drawImage(img, A4[0] - 15*mm - width, 8*mm, width=width, height=height, mask='auto')

def markdownStory(mdown):
    def match_heading(line, story, style):
        for i in range(0, 6):
            m = re.search(r'^\#{' + str(i + 1) + '}\s(.*)', line)
            if m is not None and len(m.groups()):
                story.append(Paragraph(m.group(1), style['Heading' + str(i + 1)]))
                return True
        return False

    def match_bullets(line, story, style):
        bullets = [
            u'\u25cf',      # disk
            u'\u25a0',      # square
            u'\u25c6',      # diamond
            u'\u27a4',      # arrowhead
            u'\u2605',      # star
        ]
        for i in range(len(bullets)):
            m = re.search(r'^\s{' + str(max(0, 4 * (i - 1) - 1)) + ',' + str(4 * (i + 1) - 1) + '}\*\s(.*)', line)
            if m is not None and len(m.groups()):
                story.append(Paragraph(m.group(1), style['Bullet' + (str(i + 1) if i > 0 else '')], bulletText=bullets[i]))
                return True
        return False

    style = pdfStyleSheet()
    story = []
    for line in mdown.splitlines():
        line = re.sub(r'(.*)\*{2}(.*)\*{2}(.*)', r'\1<b>\2</b>\3', line)    # replace bold (*)
        line = re.sub(r'(.*)\_{2}(.*)\_{2}(.*)', r'\1<b>\2</b>\3', line)    # replace bold (_)
        line = re.sub(r'(.*)\*{1}(.*)\*{1}(.*)', r'\1<i>\2</i>\3', line)    # replace italic (*)
        line = re.sub(r'(.*)\_{1}(.*)\_{1}(.*)', r'\1<i>\2</i>\3', line)    # replace italic (_)
        line = re.sub(                                                      # replace links
            r'\[(.*)\]\s*\((.*)\)',
            r'<link href="\2"><font color="#3a6af7">\1</font></link>',
            line
        )
        if match_heading(line, story, style):
            continue
        if match_bullets(line, story, style):
            continue
        story.append(Paragraph(line, style['BodyText']))
    return story

def pdfStyleSheet():
    """Returns a stylesheet object"""
    stylesheet = StyleSheet1()

    stylesheet.add(
        ParagraphStyle(
            name='Normal',
            fontName=tt2ps('Helvetica', 0, 0),
            fontSize=10,
            leading=12
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='NormalB',
            parent=stylesheet['Normal'],
            fontName=tt2ps('Helvetica', 1, 0)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='NormalI',
            parent=stylesheet['Normal'],
            fontName=tt2ps('Helvetica', 0, 1)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='NormalBI',
            parent=stylesheet['Normal'],
            fontName=tt2ps('Helvetica', 1, 1)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='NormalC',
            parent=stylesheet['Normal'],
            alignment=TA_CENTER
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='NormalR',
            parent=stylesheet['Normal'],
            alignment=TA_RIGHT
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='NormalBR',
            parent=stylesheet['NormalB'],
            alignment=TA_RIGHT
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='NormalBC',
            parent=stylesheet['NormalC'],
            fontName=tt2ps('Helvetica', 1, 0)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='NormalIC',
            parent=stylesheet['NormalC'],
            fontName=tt2ps('Helvetica', 0, 1)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='NormalBIC',
            parent=stylesheet['NormalC'],
            fontName=tt2ps('Helvetica', 1, 1)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='NormalBCLink',
            parent=stylesheet['NormalBC'],
            textColor=colors.HexColor('#3a6af7')
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='NormalBLink',
            parent=stylesheet['NormalB'],
            textColor=colors.HexColor('#3a6af7')
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='NormalBRLink',
            parent=stylesheet['NormalBR'],
            textColor=colors.HexColor('#3a6af7')
        )
    )

    stylesheet.add(
        ParagraphStyle(
            name='Secondary',
            fontName=tt2ps('Helvetica', 0, 0),
            fontSize=8,
            leading=10
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='SecondaryC',
            parent=stylesheet['Secondary'],
            alignment=TA_CENTER
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='SecondaryLink',
            parent=stylesheet['Secondary'],
            textColor=colors.HexColor('#3a6af7')
        )
    )

    stylesheet.add(
        ParagraphStyle(
            name='Monospace',
            fontName=tt2ps('Courier', 0, 0),
            fontSize=10,
            leading=12
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='MonospaceB',
            parent=stylesheet['Monospace'],
            fontName=tt2ps('Courier', 1, 0)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='MonospaceI',
            parent=stylesheet['Monospace'],
            fontName=tt2ps('Courier', 0, 1)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='MonospaceBI',
            parent=stylesheet['Monospace'],
            fontName=tt2ps('Courier', 1, 1)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='MonospaceC',
            parent=stylesheet['Monospace'],
            alignment=TA_CENTER
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='MonospaceBC',
            parent=stylesheet['MonospaceC'],
            fontName=tt2ps('Courier', 1, 0)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='MonospaceIC',
            parent=stylesheet['MonospaceC'],
            fontName=tt2ps('Courier', 0, 1)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='MonospaceBIC',
            parent=stylesheet['MonospaceC'],
            fontName=tt2ps('Courier', 1, 1)
        )
    )

    stylesheet.add(
        ParagraphStyle(
            name='TableHeader',
            fontName=tt2ps('Helvetica', 0, 0),
            fontSize=14,
            leading=16,
            textColor=colors.black
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='TableHeaderR',
            parent=stylesheet['TableHeader'],
            alignment=TA_RIGHT
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='TableHeaderB',
            parent=stylesheet['TableHeader'],
            fontName=tt2ps('Helvetica', 1, 0)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='TableHeaderI',
            parent=stylesheet['TableHeader'],
            fontName=tt2ps('Helvetica', 0, 1)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='TableHeaderBI',
            parent=stylesheet['TableHeader'],
            fontName=tt2ps('Helvetica', 1, 1)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='TableHeaderC',
            parent=stylesheet['TableHeader'],
            alignment=TA_CENTER
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='TableHeaderBC',
            parent=stylesheet['TableHeaderC'],
            fontName=tt2ps('Helvetica', 1, 0)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='TableHeaderIC',
            parent=stylesheet['TableHeaderC'],
            fontName=tt2ps('Helvetica', 0, 1)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='TableHeaderBIC',
            parent=stylesheet['TableHeaderC'],
            fontName=tt2ps('Helvetica', 1, 1)
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='TableHeaderBLink',
            parent=stylesheet['TableHeaderB'],
            textColor=colors.HexColor('#3a6af7')
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='TableHeaderBCLink',
            parent=stylesheet['TableHeaderBC'],
            textColor=colors.HexColor('#3a6af7')
        )
    )

    stylesheet.add(
        ParagraphStyle(
            name='ColumnHeader',
            fontName=tt2ps('Helvetica', 0, 0),
            fontSize=8,
            leading=8,
            textColor=colors.dimgray
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='ColumnHeaderC',
            parent=stylesheet['ColumnHeader'],
            alignment=TA_CENTER
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='ColumnHeaderR',
            parent=stylesheet['ColumnHeader'],
            alignment=TA_RIGHT
        )
    )

    stylesheet.add(
        ParagraphStyle(
            name='Title',
            parent=stylesheet['Normal'],
            fontName = tt2ps('Helvetica', 1, 0),
            fontSize=24,
            leading=30,
            alignment=TA_CENTER,
            spaceBefore=30,
            spaceAfter=20
            ),
        alias='title'
    )

    stylesheet.add(
        ParagraphStyle(
            name='SubTitle',
            parent=stylesheet['Normal'],
            fontName = tt2ps('Helvetica', 1, 0),
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=12
            ),
        alias='subtitle'
    )

    stylesheet.add(
        ParagraphStyle(
            name='Heading1',
            parent=stylesheet['Normal'],
            fontName = tt2ps('Helvetica', 1, 0),
            fontSize=18,
            leading=22,
            spaceBefore=12,
            spaceAfter=6
        ),
        alias='h1'
    )

    stylesheet.add(
        ParagraphStyle(
            name='Heading2',
            parent=stylesheet['Normal'],
            fontName = tt2ps('Helvetica', 0, 0),
            fontSize=16,
            leading=18,
            spaceBefore=12,
            spaceAfter=6
        ),
        alias='h2'
    )

    stylesheet.add(
        ParagraphStyle(
            name='Heading3',
            parent=stylesheet['Normal'],
            fontName = tt2ps('Helvetica', 1, 0),
            fontSize=14,
            leading=16,
            spaceBefore=12,
            spaceAfter=6
        ),
        alias='h3'
    )

    stylesheet.add(
        ParagraphStyle(
            name='Heading4',
            parent=stylesheet['Normal'],
            fontName = tt2ps('Helvetica', 1, 0),
            fontSize=12,
            leading=14,
            spaceBefore=10,
            spaceAfter=4
        ),
        alias='h4'
    )

    stylesheet.add(
        ParagraphStyle(
            name='Heading5',
            parent=stylesheet['Normal'],
            fontName = tt2ps('Helvetica', 1, 1),
            fontSize=10,
            leading=12,
            spaceBefore=8,
            spaceAfter=4
        ),
        alias='h5'
    )

    stylesheet.add(
        ParagraphStyle(
            name='BodyText',
            fontName=tt2ps('Helvetica', 0, 0),
            fontSize=12,
            leading=14,
            spaceBefore=6
        )
    )

    stylesheet.add(
        ParagraphStyle(
            name='Bullet',
            parent=stylesheet['BodyText'],
            fontName=tt2ps('Helvetica', 0, 0),
            bulletFontSize=6,
            bulletOffsetY=2,
            firstLineIndent=0,
            leftIndent=25,
            bulletIndent=10,
            spaceBefore=3
        ),
    )

    stylesheet.add(
        ParagraphStyle(
            name='Bullet1',
            parent=stylesheet['Bullet']
        )
    )

    stylesheet.add(
        ParagraphStyle(
            name='Bullet2',
            parent=stylesheet['Bullet'],
            leftIndent=40,
            bulletIndent=25,
        )
    )

    stylesheet.add(
        ParagraphStyle(
            name='Bullet3',
            parent=stylesheet['Bullet'],
            leftIndent=55,
            bulletIndent=40
        )
    )

    stylesheet.add(
        ParagraphStyle(
            name='Bullet4',
            parent=stylesheet['Bullet'],
            leftIndent=70,
            bulletIndent=55
        )
    )

    stylesheet.add(
        ParagraphStyle(
            name='MarkerBRLink',
            fontName = tt2ps('Helvetica', 1, 0),
            fontSize=20,
            leading=24,
            alignment=TA_RIGHT,
            textColor=colors.HexColor('#3a6af7')
        )
    )
    stylesheet.add(
        ParagraphStyle(
            name='MarkerBRSmallWhite',
            parent=stylesheet['MarkerBRLink'],
            fontSize=18,
            leading=23,
            spaceBefore=0,
            spaceAfter=0,
            textColor=colors.HexColor('#ffffff')
        )
    )

    return stylesheet