from django.contrib import admin
from .models import PoliticalParty,Voter

@admin.register(PoliticalParty)
class PoliticalPartyAdmin(admin.ModelAdmin):
    list_display = ('party_id', 'party_name', 'party_leader')  # ✅ Must match model fields
    search_fields = ('party_name', 'party_leader')

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ('name', 'adhaar_number', 'email', 'region', 'is_verified')
    search_fields = ('name', 'adhaar_number', 'email')

