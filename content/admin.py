from django.contrib import admin

from .models import Team, Race, RaceAssign, RaceDrawMode, Post, Skipper, Training, Category

# since we show the admin panel in an iframe, this is not needed anymore
admin.site.site_url = None

admin.site.register(Post)
admin.site.register(Team)
admin.site.register(Race)
admin.site.register(RaceAssign)
admin.site.register(RaceDrawMode)
admin.site.register(Skipper)
admin.site.register(Training)
admin.site.register(Category)
