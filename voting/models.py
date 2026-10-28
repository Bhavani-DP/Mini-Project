from django.db import models
from django.contrib.auth import get_user_model
import hashlib
import datetime


class Voter(models.Model):
    aadhar_number = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=100)
    dob = models.DateField()
    pincode = models.CharField(max_length=6)
    region = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=10)
    gender = models.CharField(
        max_length=10,
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other'),
        ],
        blank=True,
        null=True,
    )
    verified = models.BooleanField(default=False)
    face_image = models.ImageField(upload_to='voter_photos/', blank=True, null=True)
    fingerprint_data = models.BinaryField(blank=True, null=True)  # ✅ added so admin has_fingerprint works

    def __str__(self):
        # Keep admin display minimal
        return f"Voter {self.aadhar_number}"


class PoliticalParty(models.Model):
    party_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos/')
    candidate_name = models.CharField(max_length=100)
    candidate_pic = models.ImageField(upload_to='candidates/')

    def __str__(self):
        return self.name


class Vote(models.Model):
    voter_hash = models.CharField(max_length=255, default="default_hash")
    generated_signature = models.CharField(max_length=64, blank=True, null=True)
    party = models.ForeignKey(PoliticalParty, on_delete=models.CASCADE)  # stored for backend tally
    timestamp = models.DateTimeField(auto_now_add=True)
    ballot_hash = models.CharField(max_length=256)
    signature = models.TextField()
    candidate = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        # Auto-generate signature if missing
        if not self.generated_signature:
            data = f"{self.candidate}-{datetime.datetime.now().isoformat()}"
            self.generated_signature = hashlib.sha256(data.encode()).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        sig = self.generated_signature[:10] if self.generated_signature else "unspecified"
        ballot = self.ballot_hash[:10] if self.ballot_hash else "unspecified"
        return f"Vote {sig}... with ballot {ballot}..."


class Party(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.ImageField(upload_to='party_symbols/')

    def __str__(self):
        return self.name


User = get_user_model()


class WebAuthnCredential(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credential_id = models.BinaryField()
    public_key = models.BinaryField()
    sign_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class WebAuthnChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(max_length=20)  # "register" or "authenticate"