from django.db import models
from datetime import date

# for list of teams
class Team(models.Model):
    active = models.BooleanField(default=False)
    wait = models.BooleanField(default=False)
    date = models.DateField(blank=True)
    name = models.CharField(max_length=200, unique=True, blank=False)
    company = models.CharField(max_length=200, blank=False)
    contact = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=25, blank=True)

    def __str__(self):
        return self.company

# for list of races (heats and finals)
class Race(models.Model):
    name = models.CharField(max_length=20, unique=True, blank=False)
    time = models.TimeField()

    def __str__(self):
        return self.name

# for teams attending a race
class RaceAssign(models.Model):
    race_id = models.BigIntegerField(blank=False)
    team_id = models.BigIntegerField(blank=True)
    lane = models.CharField(max_length=20, blank=False)
    time = models.TimeField(null=True, blank=True)

# placeholder description for finale draw
class RaceDrawMode(models.Model):
    race_id = models.BigIntegerField(blank=False)
    desc = models.CharField(max_length=200, blank=True)
    lane = models.CharField(max_length=20, blank=False)

