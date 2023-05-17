"""
Helper functions and classes for PDF file rendering

All in here is fixed to A4 page size and the purpose of rendering
pages for the DBRegatta site and not necessarily universally usable
"""

import os

from constance import config
from django.conf import settings

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.fonts import tt2ps
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import StyleSheet1, ParagraphStyle

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
            name='NormalC',
            parent=stylesheet['Normal'],
            alignment=TA_CENTER
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
            name='TableHeader',
            fontName=tt2ps('Helvetica', 0, 0),
            fontSize=12,
            leading=14,
            textColor=colors.black
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
            name='Title',
            parent=stylesheet['Normal'],
            fontName = tt2ps('Helvetica', 1, 0),
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=6
            ),
        alias='title'
    )

    stylesheet.add(
        ParagraphStyle(
            name='Heading1',
            parent=stylesheet['Normal'],
            fontName = tt2ps('Helvetica', 0, 0),
            fontSize=16,
            fontWeight=300,
            leading=20,
            spaceAfter=6
        ),
        alias='h1'
    )

    stylesheet.add(
        ParagraphStyle(
            name='Heading2',
            parent=stylesheet['Normal'],
            fontName = tt2ps('Helvetica', 0, 0),
            fontSize=14,
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
            fontName = tt2ps('Helvetica', 1, 1),
            fontSize=12,
            leading=14,
            spaceBefore=12,
            spaceAfter=6
        ),
        alias='h3'
    )

    stylesheet.add(
        ParagraphStyle(
            name='Heading4',
            parent=stylesheet['Normal'],
            fontName = tt2ps('Helvetica', 1, 1),
            fontSize=10,
            leading=12,
            spaceBefore=10,
            spaceAfter=4
        ),
        alias='h4'
    )

    return stylesheet