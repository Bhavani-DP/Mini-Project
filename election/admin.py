from django.contrib import admin
from .models import Voter, PoliticalParty

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'gender', 'dob', 'is_verified')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('gender', 'is_verified')

@admin.register(PoliticalParty)
class PoliticalPartyAdmin(admin.ModelAdmin):
    list_display = ('party_id', 'name', 'leader')
    search_fields = ('name', 'leader')
