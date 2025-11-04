from django.db import models

class Voter(models.Model):
    uid = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=120)
    dob = models.DateField()
    email = models.EmailField(unique=True)
    region = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10, default='573201')
    phone = models.CharField(max_length=10)       
    gender = models.CharField(max_length=15) 
    profile_pic = models.ImageField(upload_to='voter_profiles/')   
    is_verified = models.BooleanField(default=False)  
    vote_done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.uid})"

class PoliticalParty(models.Model):
    party_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    leader = models.CharField(max_length=100)
    symbol = models.ImageField(upload_to='symbols/')
    candidate_pic = models.ImageField(upload_to='candidates/')

    def __str__(self):
        return self.name 

class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name='election_votes')
    party = models.ForeignKey(PoliticalParty, on_delete=models.CASCADE, related_name='election_party_votes')
    vote_time = models.CharField(max_length=120)
    hash = models.CharField(max_length=256)
    previous_hash = models.CharField(max_length=256)
    signature = models.TextField()

    def __str__(self):
        return f"Vote by {self.voter.name} for {self.party.name}"