from django.db import models
from election.models import Voter, PoliticalParty

class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name='blockchain_votes')
    party = models.ForeignKey(PoliticalParty, on_delete=models.CASCADE, related_name='blockchain_party_votes')
    vote_time = models.CharField(max_length=120)
    hash = models.CharField(max_length=256)
    previous_hash = models.CharField(max_length=256)
    signature = models.TextField()
