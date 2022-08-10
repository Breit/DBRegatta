from datetime import date, time, timedelta

# IMPORTANT: Don't change settings in here!!!
# Settings should be configurerd through the Django admin interface!

CONSTANCE_CONFIG = {
    # Global Settings
    'siteName':                 ('DBRegatta',                                   'Page Title'),
    'eventDate':                (date(2022, 1, 1),                              'Date for the DBRegatta Event'),
    'homeUrl':                  ('/',                                           'Redirect URL to Mainsite'),
    'homeIcon':                 ('dragon.svg',                                  'Icon for Redirect to Mainsite'),
    'siteLogo':                 ('usv_logo.png',                                'Main Site Logo'),
    'siteCSS':                  ('site.css',                                    'Main Site CSS'),
    'sponsorName':              ('',                                            'Sponsor Name'),
    'sponsorLogo':              ('',                                            'Sponsor Logo'),
    'sponsorUrl':               ('',                                            'Sponsor URL'),
    'ownerName':                ('USV Jena e.V. - Abteilung Kanu',              'Site Owner Name'),
    'ownerLogo':                ('usv_kanu_footer.png',                         'Site Owner Logo'),
    'ownerUrl':                 ('',                                            'Site Owner URL'),

    # Teams Settings
    'teamsNavigationCSS':       ('menu.css',                                    'CSS File for the Navigation Menu'),
    'teamsPageCSS':             ('teams.css',                                   'CSS File for Site-specific Styling'),
    'teamsTitle':               ('Teamverwaltung',                              'Menu Title for Teams Page'),
    'teamsIcon':                ('team.svg',                                    'Menu Icon for Teams Page'),
    'editTeamHeader':           ('Bearbeitung Teams',                           'Header Text for Add Team'),
    'teamListHeader':           ('Teamliste',                                   'Header Text for Teams List'),
    'activeTeams':              ('Aktive Teams',                                'Text for Active Teams Statistics'),
    'addTeam':                  ('Neues Team',                                  'Text for New Team Button'),
    'submitAddTeam':            ('Hinzufügen',                                  'Text for Save New Team Button'),
    'submitEditTeam':           ('Speichern',                                   'Text for Save Team Changes Button'),
    'submitAbort':              ('Abbrechen',                                   'Text for Cancel Button'),
    'warningDeleteTeam':        ('Team endgültig löschen?',                     'Safety Warning Message for deleting a Team'),
    'addTeamIcon':              ('add.svg',                                     'Icon for adding new Team'),
    'removeTeamIcon':           ('trash.svg',                                   'Icon for deleting Teams'),
    'activeTeamIcon':           ('active.svg',                                  'Icon for active Teams'),
    'inactiveTeamIcon':         ('inactive.svg',                                'Icon for inactive Teams'),
    'editTeamIcon':             ('edit.svg',                                    'Icon for Edit Icon'),
    'submitTeamIcon':           ('ok.svg',                                      'Icon for Submit Button'),
    'cancelTeamIcon':           ('cancel.svg',                                  'Icon for Cancel Button'),

    # Timetable Settings
    'timetableNavigationCSS':   ('menu.css',                                    'CSS File for the Navigation Menu'),
    'timetablePageCSS':         ('timetable.css',                               'CSS File for Site-specific Styling'),
    'timetableTitle':           ('Zeitplan',                                    'Menu Title for Timetable Page'),
    'timetableIcon':            ('timetable.svg',                               'Menu Icon for Timetable Page'),
    'timetableSettingsHeader':  ('Zeitplan Einstellungen',                      'Header label for Settings Section on the Timetable Page'),
    'timetableHeader':          ('Rennplan',                                    'Header Label for Timetable Page'),
    'refreshTimetableIcon':     ('expired.svg',                                 'Icon for Refresh Times Button'),
    'createTimetableIcon':      ('timetable.svg',                               'Icon for Timetable Draw Button'),
    'refreshTimetableText':     ('Zeiten aktualisieren',                        'Text for Refresh Times Button'),
    'createTimetableText':      ('Zeitplan verlosen',                           'Text for Timetable Draw Button'),
    'warningCreateTimetable':   ('Zeitplan komplett neu verlosen?',             'Warning Message for Timetable Draw'),
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
    'timetableHeaderName':      ('Lauf',                                        'Timetable Table Header for Race'),
    'timetableHeaderTeam':      ('Team',                                        'Timetable Table Header for Team Name'),
    'timetableHeaderCompany':   ('Firma',                                       'Timetable Table Header for Company Name'),
    'timetableHeaderLane':      ('Bahn',                                        'Timetable Table Header for Lane'),
    'teamCaptainsMeetingTitle': ('Team Captains Meeting am Strandschleicher',   'Text for Team Captains Meeting'),
    'victoryCeremonyTitle':     ('Siegerehrung am Strandschleicher',            'Text for Victory Ceremony'),
    'heatsTitle':               ('Vorrunde',                                    'Name for Heats'),
    'finaleTitle':              ('Finale',                                      'Name for Finale'),
    'finaleTemplate1':          ('Platz {} aus VR',                             'Template Placeholder 1 for Finale'),
    'finaleTemplate2':          ('Erster aus {}',                               'Template Placeholder 2 for Finale'),

    # Time Settings
    'timeTitle':                ('Zeiteingabe',                                 'Menu Title for Time Page'),
    'timeIcon':                 ('time.svg',                                    'Menu Icon for Time Page'),

    # Results Settings
    'resultsTitle':             ('Ergebnisse',                                  'Menu Title for Results Page'),
    'resultsIcon':              ('results.svg',                                 'Menu Icon for Results Page'),

    # Settings for Settings Page
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
            'eventDate',
            'homeUrl',
            'homeIcon',
            'siteLogo',
            'siteCSS',
            'sponsorName',
            'sponsorLogo',
            'sponsorUrl',
            'ownerName',
            'ownerLogo',
            'ownerUrl',
        ),
        'collapse': True
    },
    'Team Settings': {
        'fields': (
            'teamsNavigationCSS',
            'teamsPageCSS',
            'teamsTitle',
            'teamsIcon',
            'editTeamHeader',
            'teamListHeader',
            'activeTeams',
            'addTeam',
            'submitAddTeam',
            'submitEditTeam',
            'submitAbort',
            'warningDeleteTeam',
            'addTeamIcon',
            'removeTeamIcon',
            'activeTeamIcon',
            'inactiveTeamIcon',
            'editTeamIcon',
            'submitTeamIcon',
            'cancelTeamIcon',
        ),
        'collapse': True
    },
    'Timetable Settings': {
        'fields': (
            'timetableNavigationCSS',
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
            'timeTitle',
            'timeIcon',
        ),
        'collapse': True
    },
    'Results Settings': {
        'fields': (
            'resultsTitle',
            'resultsIcon',
        ),
        'collapse': True
    },
    'Settings Page Settings': {
        'fields': (
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
