from datetime import date, time, timedelta

# IMPORTANT: Don't change settings in here!!!
# Settings should be configurerd through the Django admin interface!

CONSTANCE_CONFIG = {
    # Global Settings
    'siteName':                 ('DBRegatta',                                   'Page Title'),
    'siteNameDesc':             ('Regatta Name',                                'Page Title Dewscription'),
    'eventDate':                (date(2022, 1, 1),                              'Date for the DBRegatta Event'),
    'eventDateDesc':            ('Regatta Datum',                               'Date for the DBRegatta Event Description'),
    'homeUrl':                  ('/',                                           'Redirect URL to Mainsite'),
    'homeIcon':                 ('dragon.svg',                                  'Icon for Redirect to Mainsite'),
    'siteLogo':                 ('usv_logo.png',                                'Main Site Logo'),
    'siteCSS':                  ('site.css',                                    'Main Site CSS'),
    'sponsorName':              ('',                                            'Sponsor Name'),
    'sponsorNameDesc':          ('Name Sponsor',                                'Sponsor Name Description'),
    'sponsorLogo':              ('',                                            'Sponsor Logo'),
    'sponsorLogoDesc':          ('Logo Sponsor',                                'Sponsor Logo Description'),
    'sponsorUrl':               ('',                                            'Sponsor URL'),
    'sponsorUrlDesc':           ('URL Sponsor',                                 'Sponsor URL Description'),
    'ownerName':                ('USV Jena e.V. - Abteilung Kanu',              'Site Owner Name'),
    'ownerNameDesc':            ('Name Veranstalter',                           'Site Owner Name Description'),
    'ownerLogo':                ('usv_kanu_footer.png',                         'Site Owner Logo'),
    'ownerLogoDesc':            ('Logo Veranstalter',                           'Site Owner Logo Description'),
    'ownerUrl':                 ('https://www.usvjena.de/kanu.html',            'Site Owner URL'),
    'ownerUrlDesc':             ('URL Veranstalter',                            'Site Owner URL Description'),

    # Teams Settings
    'teamsPageCSS':             ('teams.css',                                   'CSS File for Site-specific Styling'),
    'teamsTitle':               ('Teamverwaltung',                              'Menu Title for Teams Page'),
    'teamsIcon':                ('team.svg',                                    'Menu Icon for Teams Page'),
    'editTeamHeader':           ('Bearbeitung Teams',                           'Header Text for Add Team'),
    'teamListHeader':           ('Teamliste',                                   'Header Text for Teams List'),
    'activeTeams':              ('Aktiv',                                       'Text for Active Teams Statistics'),
    'waitlistTeams':            ('Warteliste',                                  'Text for Waitlist Teams Statistics'),
    'inactiveTeams':            ('Inaktiv',                                     'Text for Inactive Teams Statistics'),
    'totalTeams':               ('Teams gesamt',                                'Text for All Teams Statistics'),
    'addTeam':                  ('Neues Team anlegen',                          'Text for New Team Button'),
    'submitAddTeam':            ('Hinzufügen',                                  'Text for Save New Team Button'),
    'submitEditTeam':           ('Speichern',                                   'Text for Save Team Changes Button'),
    'submitAbort':              ('Abbrechen',                                   'Text for Cancel Button'),
    'warningDeleteTeam':        ('Team endgültig löschen?',                     'Safety Warning Message for deleting a Team'),
    'addTeamIcon':              ('add.svg',                                     'Icon for Adding new Team'),
    'removeTeamIcon':           ('trash.svg',                                   'Icon for Deleting Teams'),
    'activeTeamIcon':           ('active.svg',                                  'Icon for Active Teams'),
    'waitTeamIcon':             ('wait.svg',                                    'Icon for Waitlist Teams'),
    'nowaitTeamIcon':           ('nowait.svg',                                  'Icon for Teams not on Waitlist'),
    'inactiveTeamIcon':         ('inactive.svg',                                'Icon for Inactive Teams'),
    'editTeamIcon':             ('edit.svg',                                    'Icon for Edit Icon'),
    'submitTeamIcon':           ('ok.svg',                                      'Icon for Submit Button'),
    'cancelTeamIcon':           ('cancel.svg',                                  'Icon for Cancel Button'),
    'teamTableHeaderID':        ('#',                                           'Team Table Header ID'),
    'teamTableHeaderTeam':      ('Team',                                        'Team Table Header Team'),
    'teamTableHeaderCompany':   ('Firma',                                       'Team Table Header Company'),
    'teamTableHeaderCaptain':   ('Team Captain',                                'Team Table Header Team Captain'),
    'teamTableHeaderEmail':     ('Email',                                       'Team Table Header Email'),
    'teamTableHeaderPhone':     ('Telefon',                                     'Team Table Header Phone'),
    'teamTableHeaderDate':      ('Anmeldung',                                   'Team Table Header Date'),
    'teamTableHeaderOptions':   ('Bearbeiten',                                  'Team Table Header Edit'),

    # Timetable Settings
    'timetablePageCSS':         ('timetable.css',                               'CSS File for Site-specific Styling'),
    'timetableTitle':           ('Zeitplan',                                    'Menu Title for Timetable Page'),
    'timetableIcon':            ('timetable.svg',                               'Menu Icon for Timetable Page'),
    'timetableSettingsHeader':  ('Zeitplan Einstellungen',                      'Header Label for Settings Section on the Timetable Page'),
    'timetableHeader':          ('Rennplan',                                    'Header Label for Timetable Page'),
    'refreshTimetableIcon':     ('expired.svg',                                 'Icon for Refresh Times Button'),
    'createTimetableIcon':      ('timetable.svg',                               'Icon for Timetable Draw Button'),
    'refreshTimetableText':     ('Zeiten aktualisieren',                        'Text for Refresh Times Button'),
    'createTimetableText':      ('Zeitplan verlosen',                           'Text for Timetable Draw Button'),
    'lanesPerRace':             (3,                                             'Lanes per Race'),
    'lanesPerRaceMin':          (1,                                             'Minimum Lanes per Race'),
    'lanesPerRaceMax':          (10,                                            'Maximum Lanes per Race'),
    'lanesPerRaceDesc':         ('Anzahl Bahnen',                               'Description Lanes per Race'),
    'heatCount':                (2,                                             'Rounds of Heats'),
    'heatCountMin':             (1,                                             'Minimum Rounds of Heats'),
    'heatCountMax':             (5,                                             'Maximum Rounds of Heats'),
    'heatCountDesc':            ('Anzahl Vorrunden',                            'Description Rounds of Heats'),
    'intervalHeat':             (timedelta(minutes=15),                         'Interval between Races in the Heats'),
    'intervalHeatDesc':         ('Rennintervall Vorrunde',                      'Description for Interval between Races in the Heats'),
    'intervalFinal':            (timedelta(minutes=15),                         'Interval between Races in the Finale'),
    'intervalFinalDesc':        ('Rennintervall Finale',                        'Description for Interval between Races in the Finale'),
    'timeBegin':                (time(hour=10, minute=00),                      'Beginning Time for the Race Schedule'),
    'timeBeginDesc':            ('Beginn Programm',                             'Description for Beginning Time for the Race Schedule'),
    'offsetHeat':               (timedelta(minutes=60),                         'Timeoffset between Team Captains Meeting and Start of the Heats'),
    'offsetHeatDesc':           ('Pause vor Vorrunde',                          'Description for Timeoffset between Team Captains Meeting and Start of the Heats'),
    'offsetFinale':             (timedelta(minutes=45),                         'Timeoffset between last Race from Heats to the Start of the Finale'),
    'offsetFinaleDesc':         ('Pause vor Finale',                            'Description for Timeoffset between last Race from Heats to the Start of the Finale'),
    'offsetCeremony':           (timedelta(minutes=30),                         'Timeoffset between last Race and Victory Ceremony'),
    'offsetCeremonyDesc':       ('Pause vor Siegerehrung',                      'Description for Timeoffset between last Race and Victory Ceremony'),
    'heatPrefix':               ('V',                                           'Prefix for Heat Race Names'),
    'finalPrefix':              ('E',                                           'Prefix for Finale Race Names'),
    'timetableHeaderTime':      ('Startzeit',                                   'Timetable Table Header for Time'),
    'timetableHeaderName':      ('Rennen',                                      'Timetable Table Header for Race'),
    'timetableHeaderTeam':      ('Team',                                        'Timetable Table Header for Team Name'),
    'timetableHeaderCompany':   ('Firma',                                       'Timetable Table Header for Company Name'),
    'timetableHeaderLane':      ('Bahn',                                        'Timetable Table Header for Lane'),
    'teamCaptainsMeetingTitle': ('Team Captains Meeting am Strandschleicher',   'Text for Team Captains Meeting'),
    'victoryCeremonyTitle':     ('Siegerehrung am Strandschleicher',            'Text for Victory Ceremony'),
    'heatsTitle':               ('Vorrunde',                                    'Name for Heats'),
    'finaleTitle':              ('Finale',                                      'Name for Finale'),
    'finaleTemplate1':          ('Platz {} aus VR',                             'Template Placeholder 1 for Finale'),
    'finaleTemplate2':          ('Erster aus {}',                               'Template Placeholder 2 for Finale'),
    'warningCreateTimetable':   ('Zeitplan komplett neu verlosen? Alle Ergebnisse und eingegebenen Zeiten werden damit verworfen!', 'Warning Message for Timetable Draw'),

    # Time Settings
    'timesPageCSS':             ('times.css',                                   'CSS File for Site-specific Styling'),
    'timeTitle':                ('Zeiteingabe',                                 'Menu Title for Time Page'),
    'timeRaceDesc':             ('Rennen',                                      'Text for Race Select Drop-Down'),
    'timesHeader':              ('Zeiteingabe',                                 'Header Label for Time Entry on Time Page'),
    'timesTableHeader':         ('Ergebnisliste',                               'Header Label for Race Results on Time Page'),
    'timeIcon':                 ('time.svg',                                    'Menu Icon for Time Page'),
    'timesHeaderTime':          ('Zeit',                                        'Header Text for Time Column'),
    'timesHeaderPlace':         ('Platz',                                       'Header Text for Place Column'),
    'refreshTimesText':         ('Zeiten eintragen',                            'Text for Refresh Times Button'),

    # Trainings Settings
    'trainingsPageCSS':         ('trainings.css',                               'CSS File for Site-specific Styling'),
    'trainingsTitle':           ('Trainings',                                   'Menu Title for Trainings Page'),
    'trainingsIcon':            ('rafting.svg',                                 'Menu Icon for Trainings Page'),

    # Results Settings
    'resultsPageCSS':           ('results.css',                                 'CSS File for Site-specific Styling'),
    'resultsTitle':             ('Ergebnisse',                                  'Menu Title for Results Page'),
    'resultsIcon':              ('results.svg',                                 'Menu Icon for Results Page'),
    'resultsTableHeader':       ('Ergebnisliste',                               'Header Label for Race Results on Results Page'),

    # Display Page Settings
    'displayPageCSS':           ('display.css',                                 'CSS File for Site-specific Styling'),
    'displayTitle':             ('Race Monitor',                                'Menu Title for Display Page'),
    'displayIcon':              ('billboard.svg',                               'Menu Icon for Display Page'),
    'displayInterval':          (10000,                                         'Time in Milliseconds for Slides on Display Page'),
    'displayIntervalDesc':      ('Monitor Slide Intervall',                     'Description for Settings Page for Slides Interval on Display Page'),
    'displayRankings':          ('Rangliste Vorrunde',                          'Rankings Header on Display Page'),
    'displayRank':              ('Rang',                                        'Rank Header on Display Page'),
    'displaySumTime':           ('Zeitsumme',                                   'Total Time Header on Display Page'),

    # Settings for Settings Page
    'settingsPageCSS':          ('settings.css',                                'CSS File for Site-specific Styling'),
    'settingsTitle':            ('Einstellungen',                               'Menu Title for Settings Page'),
    'settingsIcon':             ('settings.svg',                                'Menu Icon for Settings Page'),

    # Settings for Admin Panel
    'adminTitle':               ('Admin Panel',                                 'Menu Title for Admin Panel Page'),
    'adminIcon':                ('django_logo.svg',                             'Menu Icon for Admin Panel Page'),
}

CONSTANCE_CONFIG_FIELDSETS = {
    'Global Settings': {
        'fields': (
            'siteName',
            'siteNameDesc',
            'eventDate',
            'eventDateDesc',
            'homeUrl',
            'homeIcon',
            'siteLogo',
            'siteCSS',
            'sponsorName',
            'sponsorNameDesc',
            'sponsorLogo',
            'sponsorLogoDesc',
            'sponsorUrl',
            'sponsorUrlDesc',
            'ownerName',
            'ownerNameDesc',
            'ownerLogo',
            'ownerLogoDesc',
            'ownerUrl',
            'ownerUrlDesc',
        ),
        'collapse': True
    },
    'Team Settings': {
        'fields': (
            'teamsPageCSS',
            'teamsTitle',
            'teamsIcon',
            'editTeamHeader',
            'teamListHeader',
            'activeTeams',
            'inactiveTeams',
            'waitlistTeams',
            'totalTeams',
            'addTeam',
            'submitAddTeam',
            'submitEditTeam',
            'submitAbort',
            'warningDeleteTeam',
            'addTeamIcon',
            'removeTeamIcon',
            'activeTeamIcon',
            'waitTeamIcon',
            'nowaitTeamIcon',
            'inactiveTeamIcon',
            'editTeamIcon',
            'submitTeamIcon',
            'cancelTeamIcon',
            'teamTableHeaderID',
            'teamTableHeaderTeam',
            'teamTableHeaderCompany',
            'teamTableHeaderCaptain',
            'teamTableHeaderEmail',
            'teamTableHeaderPhone',
            'teamTableHeaderDate',
            'teamTableHeaderOptions',
        ),
        'collapse': True
    },
    'Timetable Settings': {
        'fields': (
            'timetablePageCSS',
            'timetableTitle',
            'timetableIcon',
            'timetableSettingsHeader',
            'timetableHeader',
            'refreshTimetableIcon',
            'createTimetableIcon',
            'refreshTimetableText',
            'createTimetableText',
            'warningCreateTimetable',
            'lanesPerRace',
            'lanesPerRaceMin',
            'lanesPerRaceMax',
            'lanesPerRaceDesc',
            'heatCount',
            'heatCountMin',
            'heatCountMax',
            'heatCountDesc',
            'intervalHeat',
            'intervalHeatDesc',
            'intervalFinal',
            'intervalFinalDesc',
            'timeBegin',
            'timeBeginDesc',
            'offsetHeat',
            'offsetHeatDesc',
            'offsetFinale',
            'offsetFinaleDesc',
            'offsetCeremony',
            'offsetCeremonyDesc',
            'heatPrefix',
            'finalPrefix',
            'timetableHeaderTime',
            'timetableHeaderName',
            'timetableHeaderTeam',
            'timetableHeaderCompany',
            'timetableHeaderLane',
            'teamCaptainsMeetingTitle',
            'victoryCeremonyTitle',
            'heatsTitle',
            'finaleTitle',
            'finaleTemplate1',
            'finaleTemplate2',
        ),
        'collapse': True
    },
    'Time Settings': {
        'fields': (
            'timesPageCSS',
            'timeTitle',
            'timeRaceDesc',
            'timesHeader',
            'timesTableHeader',
            'timesHeaderPlace',
            'timeIcon',
            'timesHeaderTime',
            'refreshTimesText',
        ),
        'collapse': True
    },
    'Trainings Settings': {
        'fields': (
            'trainingsPageCSS',
            'trainingsTitle',
            'trainingsIcon',
        ),
        'collapse': True
    },
    'Results Settings': {
        'fields': (
            'resultsPageCSS',
            'resultsTitle',
            'resultsIcon',
            'resultsTableHeader',
        ),
        'collapse': True
    },
    'Display Settings': {
        'fields': (
            'displayPageCSS',
            'displayTitle',
            'displayIcon',
            'displayInterval',
            'displayIntervalDesc',
            'displayRankings',
            'displayRank',
            'displaySumTime',
        ),
        'collapse': True
    },
    'Settings Page Settings': {
        'fields': (
            'settingsPageCSS',
            'settingsTitle',
            'settingsIcon',
        ),
        'collapse': True
    },
    'Admin Panel Settings': {
        'fields': (
            'adminTitle',
            'adminIcon',
        ),
        'collapse': True
    }
}
