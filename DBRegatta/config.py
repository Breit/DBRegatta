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
    'questionIcon':             ('question.svg',                                'Icon for Modal Questions'),
    'submitAbort':              ('Abbrechen',                                   'Text for Cancel Button'),
    'overscan':                 (0,                                             'Overscan Margin for TV Displays'),
    'overscanDesc':             ('Overscan Kompensation',                       'Label Text for Overscan Margin for TV Displays Control'),
    'overscanMax':              (5,                                             'Maximum Overscan Margin for TV Displays'),
    'domain':                   ('',                                            'Domain Name of the Site'),

    # Teams Settings
    'teamsPageCSS':             ('teams.css',                                   'CSS File for Site-specific Styling'),
    'teamsPageJS':              ('teams.js',                                    'JS File for Site-specific Data Handling'),
    'teamsTitle':               ('Teamverwaltung',                              'Menu Title for Teams Page'),
    'teamsIcon':                ('team.svg',                                    'Menu Icon for Teams Page'),
    'addTeamHeader':            ('Team hinzufügen',                             'Header Text for Add Team'),
    'editTeamHeader':           ('Team bearbeiten',                             'Header Text for Edit Team'),
    'teamListHeader':           ('Teamliste',                                   'Header Text for Teams List'),
    'activeTeams':              ('Aktiv',                                       'Text for Active Teams Statistics'),
    'waitlistTeams':            ('Warteliste',                                  'Text for Waitlist Teams Statistics'),
    'inactiveTeams':            ('Inaktiv',                                     'Text for Inactive Teams Statistics'),
    'totalTeams':               ('Teams gesamt',                                'Text for All Teams Statistics'),
    'addTeam':                  ('Neues Team anlegen',                          'Text for New Team Button'),
    'submitAddTeam':            ('Hinzufügen',                                  'Text for Save New Team Button'),
    'submitEditTeam':           ('Speichern',                                   'Text for Save Team Changes Button'),
    'deleteTeam':               ('Team löschen',                                'Text for Delete Team Button'),
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
    'teamTableHeaderAddress':   ('Adresse',                                     'Team Table Header Address'),
    'teamTableHeaderOptions':   ('Bearbeiten',                                  'Team Table Header Edit'),
    'placeholderTeamActive':    ('Team aktiv',                                  'Placeholder Text for Teams Form: Active Status'),
    'placeholderTeamWaitlist':  ('Warteliste',                                  'Placeholder Text for Teams Form: Waitlist Status'),
    'placeholderTeamSignupDate':('Anmeldedatum',                                'Placeholder Text for Teams Form: Signup Date'),
    'placeholderTeamName':      ('Teamname',                                    'Placeholder Text for Teams Form: Team Name'),
    'placeholderTeamCompany':   ('Firma',                                       'Placeholder Text for Teams Form: Team Company'),
    'placeholderTeamCaptain':   ('Kontakt / Team Captain',                      'Placeholder Text for Teams Form: Team Captain'),
    'placeholderTeamEmail':     ('Email Adresse',                               'Placeholder Text for Teams Form: Team Email'),
    'placeholderTeamPhone':     ('Telefonnummer',                               'Placeholder Text for Teams Form: Team Phone Number'),
    'placeholderTeamAddress':   ('Adresse',                                     'Placeholder Text for Teams Form: Team Address'),
    'warningDeleteTeam':        ('Team endgültig löschen?\nAlle Rennauslosungen für dieses Team und alle Ergebnisse gehen dabei ebenfalls verloren.', 'Safety Warning Message for deleting a Team'),

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
    'timetablePostDesc':        ('Mitteilungen zum Rennplan',                   'Description for Post on Timetable Control'),
    'heatPrefix':               ('V',                                           'Prefix for Heat Race Names'),
    'finalPrefix':              ('E',                                           'Prefix for Finale Race Names'),
    'timetableHeaderTime':      ('Startzeit',                                   'Timetable Table Header for Time'),
    'timetableHeaderName':      ('Rennen',                                      'Timetable Table Header for Race'),
    'timetableHeaderTeam':      ('Team',                                        'Timetable Table Header for Team Name'),
    'timetableHeaderCompany':   ('Firma',                                       'Timetable Table Header for Company Name'),
    'timetableHeaderSkipper':   ('Steuer',                                      'Timetable Table Header for Skipper Column'),
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
    'timesHeaderRank':          ('Rang',                                        'Header Text for Total Rank Column'),
    'timesHeaderSkipper':       ('Steuer',                                      'Header Text for Skipper Column'),
    'refreshTimesText':         ('Zeiten eintragen',                            'Text for Refresh Times Button'),

    # Trainings Settings
    'trainingsPageCSS':         ('trainings.css',                               'CSS File for Site-specific Styling'),
    'trainingsTitle':           ('Trainings',                                   'Menu Title for Trainings Page'),
    'trainingsIcon':            ('rafting.svg',                                 'Menu Icon for Trainings Page'),

    # Skippers Settings
    'skippersPageCSS':          ('skippers.css',                                'CSS File for Site-specific Styling'),
    'skippersTitle':            ('Steuerleute',                                 'Menu Title for Skippers Page'),
    'activeSkipperTitle':       ('Aktiv',                                       'Table Title for Active Skippers'),
    'inactiveSkipperTitle':     ('Inaktiv',                                     'Table Title for Inactive Skippers'),
    'skippersIcon':             ('skippers.svg',                                'Menu Icon for Skippers Page'),
    'skippersEditHeading':      ('Steuerleute bearbeiten',                      'Heading for Editing Skippers on Skippers Page'),
    'skippersListHeading':      ('Liste Steuerleute',                           'Menu Title for Skippers Page'),
    'placeholderSkipperName':   ('Anzeigename',                                 'Nickname Placeholder Text for Skippers Page'),
    'placeholderSkipperFName':  ('Vorname',                                     'First Name Placeholder Text for Skippers Page'),
    'placeholderSkipperLName':  ('Nachname',                                    'Last Name Placeholder Text for Skippers Page'),
    'placeholderSkipperEmail':  ('Email Adresse',                               'Email Placeholder Text for Skippers Page'),
    'placeholderSkipperActive': ('Aktiv',                                       'Active Status Placeholder Text for Skippers Page'),
    'skipperTableHeaderOptions':('Bearbeiten',                                  'Options Header Text for Skippers Table on Skippers Page'),
    'addSkipper':               ('Steuermann hinzufügen',                       'Text for Add Skipper Button'),
    'deleteSkipper':            ('Steuermann löschen',                          'Text for Delete Skipper Button'),
    'warningDeleteSkipper':     ('Steuermann endgültig löschen?',               'Safety Warning Message for Deleting a Skipper'),
    'skipperTableHeaderID':     ('#',                                           'Skippers Table Header ID'),

    # Results Settings
    'resultsPageCSS':           ('results.css',                                 'CSS File for Site-specific Styling'),
    'resultsTitle':             ('Ergebnisse',                                  'Menu Title for Results Page'),
    'resultsIcon':              ('results.svg',                                 'Menu Icon for Results Page'),
    'resultsTableHeader':       ('Ergebnisliste',                               'Header Label for Race Results on Results Page'),
    'activateResults':          (False,                                         'Toggle Display Results Page for Unauthenticated Users'),
    'activateResultsDesc':      ('Ergebnisse anonym',                           'Description for Toggle Display Results Page for Unauthenticated Users'),
    'activeResultsDesc':        ('anzeigen',                                    'Description for active Toggle Display Results Page for Unauthenticated Users'),
    'inactiveResultsDesc':      ('verbergen',                                   'Description for inactive Toggle Display Results Page for Unauthenticated Users'),

    # Display Page Settings
    'displayPageCSS':           ('display.css',                                 'CSS File for Site-specific Styling'),
    'displayTitle':             ('Race Monitor',                                'Menu Title for Display Page'),
    'displayIcon':              ('billboard.svg',                               'Menu Icon for Display Page'),
    'displayInterval':          (10000,                                         'Time Interval for Slides on Display Page in Milliseconds'),
    'displayIntervalDesc':      ('Monitor Slide Intervall',                     'Description for Settings Page for Slides Interval on Display Page'),
    'displayDataRefresh':       (60000,                                         'Content Refresh Timer for Data on Display Page in Milliseconds'),
    'displayDataRefreshDesc':   ('Monitor Data Refresh',                        'Description for Content Refresh Timer for Data on Display Page'),
    'displayRankings':          ('Rangliste',                                   'Rankings Header on Display Page'),
    'displayRank':              ('Rang',                                        'Rank Header on Display Page'),
    'displaySumTime':           ('Zeitsumme',                                   'Total Time Header on Display Page'),
    'displayBestTime':          ('Schnellste Zeit',                             'Best Time Header on Display Page'),
    'displayFinalTime':         ('Zeit Finale',                                 'Finale Time Header on Display Page'),
    'displayRaces':             ('Finalrennen',                                 'Finale Races Count Header on Display Page'),
    'maxRacesPerPage':          (8,                                             'Maximum Number of Races to Show on Display Page'),
    'maxRacesPerPageDesc':      ('Max. Rennen pro Seite',                       'Description for Maximum Number of Races to Show on Display Page'),
    'racesPerPageDesc':         ('Teil',                                        'Descriptive Text If Races Are Split Over More Pages on Display Page'),
    'anonymousMonitor':         (True,                                          'Allow Race Monitor Page for Unauthenticated Users'),
    'anonymousMonitorDesc':     ('Race Monitor annonym',                        'Description for Allow Race Monitor Page for Unauthenticated Users'),
    'liveResultsHint':          ('Live-Ergebnisse auf:',                        'Live Results Hint at the Bottom of the Display Page'),
    'liveResultsHintDesc':      ('Hinweistext für Live-Ergebnisse Race Monitor','Description for Live Results Hint at the Bottom of the Display Page'),
    'liveResultsDomainDesc':    ('Link zu Live-Ergebnissen Race Monitor',       'Description for Live Results Hint Domain at the Bottom of the Display Page'),

    # Settings for Settings Page
    'settingsPageCSS':          ('settings.css',                                'CSS File for Site-specific Styling'),
    'settingsTitle':            ('Einstellungen',                               'Menu Title for Settings Page'),
    'settingsHeaderRegatta':    ('Regatta',                                     'Section Title for Regatta Settings on Settings Page'),
    'settingsHeaderAccess':     ('Zugriffsrechte',                              'Section Title for Access Settings on Settings Page'),
    'settingsHeaderMonitor':    ('Race Monitor',                                'Section Title for Race Monitor Settings on Settings Page'),
    'settingsHeaderFooter':     ('Fußzeile',                                    'Section Title for Footer Settings on Settings Page'),
    'settingsIcon':             ('settings.svg',                                'Menu Icon for Settings Page'),
    'settingsAdvancedHeader':   ('Entwickleroptionen',                          'Header for Advanced Settings'),
    'placeholderPostContent':   ('Mitteilung',                                  'Placeholder Text for Post Content Control'),
    'devOptionsTimetable':      ('Zeitplan / Zeiteingabe',                      'Header for Advanced Settings Timetable'),
    'devOptionsData':           ('Teams / Steuerleute',                         'Header for Advanced Settings Data'),
    'resetFinals':              ('Finale zurücksetzen',                         'Button Text for Reset Finals Button'),
    'resetFinalsIcon':          ('deleteTable.svg',                             'Button Icon for Reset Finals Button'),
    'resetHeats':               ('Vorrunde zurücksetzen',                       'Button Text for Reset Heats Button'),
    'resetHeatsIcon':           ('trashTable.svg',                              'Button Icon for Reset Heats Button'),
    'resetTeams':               ('Teams löschen',                               'Button Text for Delete Teams Button'),
    'resetTeamsIcon':           ('trashTeam.svg',                               'Button Icon for Delete Teams Button'),
    'resetSkippers':            ('Steuerleute löschen',                         'Button Text for Delete Skippers Button'),
    'resetSkippersIcon':        ('trashSkippers.svg',                           'Button Icon for Delete Skippers Button'),
    'devOptionsDatabase':       ('Datenbank',                                   'Header for Advanced Settings Database'),
    'backupDatabase':           ('Backup Datenbank',                            'Button Text for Database Backup Button'),
    'backupDatabaseIcon':       ('backupDB.svg',                                'Button Icon for Database Backup Button'),
    'noBackup':                 ('Kein Backup vorhanden!',                      'Text for No Database Backup Found'),
    'warningResetHeats':        ('Alle Zeiten der Vorrunde endgültig löschen?\n\nDies schließt auch alle Zeiten der Finals und die Auslosung der Finals mit ein!',                                                                                                          'Warning Message for Reset Heats Button'),
    'warningResetFinals':       ('Alle Zeiten der Finals endgültig löschen?\n\nDie Auslosung der Finals wird damit ebenfalls zurückgesetzt!\nDie Platzierungen basierend auf der Rangliste aus der Vorrunde wird neu gesetzt.\nDie Zeiten der Vorrunde bleiben bestehen.',  'Warning Message for Reset Finals Button'),
    'warningResetTeams':        ('Alle Teams aus der Datenbank endgültig löschen?\n\nDies schließt auch die Löschung alle Rennen inklusive der eingetragenen Zeiten mit ein!',                                                                                              'Warning Message for Reset Teams Button'),
    'warningResetSkippers':     ('Alle Steuerleute aus der Datenbank endgültig löschen?\n\nDie Zuordnung der Steuerleute zu den einzelnen Rennen wird ebenfalls aufgehoben durch diesen Schritt!',                                                                          'Warning Message for Reset Skippers Button'),

    # Settings for Admin Panel
    'adminTitle':               ('Admin Panel',                                 'Menu Title for Admin Panel Page'),
    'adminIcon':                ('django_logo.svg',                             'Menu Icon for Admin Panel Page'),

    # Login Settings
    'loginButtonText':          ('Anmelden',                                    'Button Text for Login Button'),
    'logoutButtonText':         ('Abmelden',                                    'Button Text for Logout Button'),
    'loginIcon':                ('login.svg',                                   'Button Image for Login Button'),
    'logoutIcon':               ('logout.svg',                                  'Button Image for Logout Button'),
    'loginUserName':            ('Benutzername',                                'Login Form Placeholder for User Name'),
    'loginPassword':            ('Passwort',                                    'Login Form Placeholder for Password'),
    'loginGreeting1':           ('Hallo',                                       'Login Greeting Part #1'),
    'loginGreeting2':           (', du bist erfolgreich angemeldet!',           'Login Greeting Part #2'),

    # Impressum Setings
    'impressumPageCSS':         ('impressum.css',                               'CSS File for Site-specific Styling'),
    'impressumPageJS':          ('impressum.js',                                'JS File for Site-specific Rendering'),
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
            'questionIcon',
            'submitAbort',
            'overscan',
            'overscanDesc',
            'overscanMax',
            'domain',
        ),
        'collapse': True
    },
    'Team Settings': {
        'fields': (
            'teamsPageCSS',
            'teamsPageJS',
            'teamsTitle',
            'teamsIcon',
            'addTeamHeader',
            'editTeamHeader',
            'teamListHeader',
            'activeTeams',
            'inactiveTeams',
            'waitlistTeams',
            'totalTeams',
            'addTeam',
            'submitAddTeam',
            'submitEditTeam',
            'deleteTeam',
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
            'teamTableHeaderAddress',
            'teamTableHeaderOptions',
            'placeholderTeamActive',
            'placeholderTeamWaitlist',
            'placeholderTeamSignupDate',
            'placeholderTeamName',
            'placeholderTeamCompany',
            'placeholderTeamCaptain',
            'placeholderTeamEmail',
            'placeholderTeamPhone',
            'placeholderTeamAddress',
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
            'timetablePostDesc',
            'heatPrefix',
            'finalPrefix',
            'timetableHeaderTime',
            'timetableHeaderName',
            'timetableHeaderTeam',
            'timetableHeaderCompany',
            'timetableHeaderSkipper',
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
            'timesHeaderRank',
            'timesHeaderSkipper',
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
    'Skippers Settings': {
        'fields': (
            'skippersPageCSS',
            'skippersTitle',
            'activeSkipperTitle',
            'inactiveSkipperTitle',
            'skippersIcon',
            'skippersEditHeading',
            'skippersListHeading',
            'placeholderSkipperName',
            'placeholderSkipperFName',
            'placeholderSkipperLName',
            'placeholderSkipperEmail',
            'placeholderSkipperActive',
            'skipperTableHeaderOptions',
            'addSkipper',
            'deleteSkipper',
            'warningDeleteSkipper',
            'skipperTableHeaderID',
        ),
        'collapse': True
    },
    'Results Settings': {
        'fields': (
            'resultsPageCSS',
            'resultsTitle',
            'resultsIcon',
            'resultsTableHeader',
            'activateResults',
            'activateResultsDesc',
            'activeResultsDesc',
            'inactiveResultsDesc',
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
            'displayDataRefresh',
            'displayDataRefreshDesc',
            'displayRankings',
            'displayRank',
            'displaySumTime',
            'displayBestTime',
            'displayRaces',
            'displayFinalTime',
            'maxRacesPerPage',
            'maxRacesPerPageDesc',
            'racesPerPageDesc',
            'anonymousMonitor',
            'anonymousMonitorDesc',
            'liveResultsHint',
            'liveResultsHintDesc',
            'liveResultsDomainDesc',
        ),
        'collapse': True
    },
    'Settings Page Settings': {
        'fields': (
            'settingsPageCSS',
            'settingsTitle',
            'settingsHeaderRegatta',
            'settingsHeaderAccess',
            'settingsHeaderMonitor',
            'settingsHeaderFooter',
            'settingsIcon',
            'settingsAdvancedHeader',
            'placeholderPostContent',
            'devOptionsTimetable',
            'devOptionsData',
            'devOptionsDatabase',
            'resetFinals',
            'resetFinalsIcon',
            'resetHeats',
            'resetHeatsIcon',
            'resetTeams',
            'resetTeamsIcon',
            'resetSkippers',
            'resetSkippersIcon',
            'backupDatabase',
            'backupDatabaseIcon',
            'noBackup',
            'warningResetHeats',
            'warningResetFinals',
            'warningResetTeams',
            'warningResetSkippers',
        ),
        'collapse': True
    },
    'Admin Panel Settings': {
        'fields': (
            'adminTitle',
            'adminIcon',
        ),
        'collapse': True
    },
    'Login Settings': {
        'fields': (
            'loginButtonText',
            'logoutButtonText',
            'loginIcon',
            'logoutIcon',
            'loginUserName',
            'loginPassword',
            'loginGreeting1',
            'loginGreeting2',
        ),
        'collapse': True
    },
    'Impressum Settings': {
        'fields': (
            'impressumPageCSS',
            'impressumPageJS',
        ),
        'collapse': True
    }
}
