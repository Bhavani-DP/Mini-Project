from django.db import models

class Voter(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    adhaar_number = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=100)
    dob = models.DateField()
    email = models.EmailField()
    region = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.adhaar_number})"


class PoliticalParty(models.Model):
    party_id = models.CharField(max_length=10, unique=True)
    party_name = models.CharField(max_length=100)
    party_leader = models.CharField(max_length=100)
    party_symbol = models.ImageField(upload_to='party_symbols/', blank=True, null=True)
    candidate_pic = models.ImageField(upload_to='candidate_pics/', blank=True, null=True)

    def __str__(self):
        return self.party_name


class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name='election_votes')
    party = models.ForeignKey(PoliticalParty, on_delete=models.CASCADE, related_name='election_party_votes')
    vote_time = models.CharField(max_length=120)
    hash = models.CharField(max_length=256)
    previous_hash = models.CharField(max_length=256)
    signature = models.TextField()

    def __str__(self):
        return f"Vote by {self.voter.name} for {self.party.party_name}"