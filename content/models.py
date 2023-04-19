from django.db import models
from django.core.validators import MaxLengthValidator

# for list of teams
class Team(models.Model):
    active = models.BooleanField(default=False)
    wait = models.BooleanField(default=False)
    position = models.PositiveSmallIntegerField(blank=False, unique=True, null=True)
    date = models.DateField(blank=False)
    name = models.CharField(max_length=200, unique=True, blank=False)
    company = models.CharField(max_length=200, blank=False)
    contact = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=25, blank=True)
    address = models.TextField(max_length=500, blank=True, validators=[MaxLengthValidator(500)])

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
    team_id = models.BigIntegerField(blank=True, null=True)
    skipper_id = models.BigIntegerField(blank=True, null=True)
    lane = models.CharField(max_length=20, blank=False)
    time = models.FloatField(null=False, blank=False, default=0.0)

# for finale draw
class RaceDrawMode(models.Model):
    race_id = models.BigIntegerField(blank=False)
    desc = models.CharField(max_length=200, blank=True)
    lane = models.CharField(max_length=20, blank=False)

# for post on timetable page
class Post(models.Model):
    enable = models.BooleanField(default=False)
    site = models.CharField(unique=True, max_length=20, blank=False)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.site

# for skippers page
class Skipper(models.Model):
    name = models.CharField(unique=True, max_length=20, blank=False)
    fname = models.CharField(max_length=100, blank=True)
    lname = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=False)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name

# for trainings page
class Training(models.Model):
    date = models.DateField(blank=False)
    time = models.TimeField(blank=False)
    skipper_id = models.BigIntegerField(blank=False, null=True)
    team_id = models.BigIntegerField(blank=False, null=True)
    notes = models.TextField(blank=True, null=True)
