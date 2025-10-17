from django.db import models

class Voter(models.Model):
    aadhar_number = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=100)
    dob = models.DateField()
    pincode = models.CharField(max_length=6)
    region = models.CharField(max_length=100)
    email = models.EmailField()
    profile_pic = models.ImageField(upload_to='profiles/')
    vote_done = models.BooleanField(default=False)

class PoliticalParty(models.Model):
    party_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos/')
    candidate_name = models.CharField(max_length=100)
    candidate_pic = models.ImageField(upload_to='candidates/')

class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    party = models.ForeignKey(PoliticalParty, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    ballot_hash = models.CharField(max_length=256)
    signature = models.TextField()