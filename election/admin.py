from django.contrib import admin
<<<<<<< HEAD
from .models import PoliticalParty,Voter

@admin.register(PoliticalParty)
class PoliticalPartyAdmin(admin.ModelAdmin):
    list_display = ('party_id', 'party_name', 'party_leader')  # ✅ Must match model fields
    search_fields = ('party_name', 'party_leader')

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ('name', 'adhaar_number', 'email', 'region', 'is_verified')
    search_fields = ('name', 'adhaar_number', 'email')

=======
from .models import Voter, PoliticalParty, Vote

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'gender', 'dob', 'is_verified')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('gender', 'is_verified')

@admin.register(PoliticalParty)
class PoliticalPartyAdmin(admin.ModelAdmin):
    list_display = ('party_id', 'name', 'leader')
    search_fields = ('name', 'leader', 'party_id')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'party', 'vote_time', 'hash')
    search_fields = ('voter__name', 'party__name', 'hash')
    list_filter = ('vote_time',)
>>>>>>> ac466ea (Initial commit with Aadhaar and OTP flow)
