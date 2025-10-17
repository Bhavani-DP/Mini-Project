from django.contrib import admin
from .models import Voter, PoliticalParty, Vote

admin.site.register(Voter)
admin.site.register(PoliticalParty)
admin.site.register(Vote)