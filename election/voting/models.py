from django.db import models

class Voter(models.Model):
    adhaar_number = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=100)
    dob = models.DateField()
    epic = models.CharField(max_length=20)
    state = models.CharField(max_length=100)
    email = models.EmailField()
    vote_done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.adhaar_number})"
