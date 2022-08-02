from django.db import models

class Team(models.Model):
    active = models.BooleanField(default=False)
    name = models.CharField(max_length=200, unique=True, blank=False)
    company = models.CharField(max_length=200, blank=False)
    contact = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return self.company
