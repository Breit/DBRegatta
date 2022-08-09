from django.contrib import admin

from .models import Team, Race, RaceAssign, RaceDrawMode

admin.site.register(Team)
admin.site.register(Race)
admin.site.register(RaceAssign)
admin.site.register(RaceDrawMode)