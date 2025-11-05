from django import forms
from .models import Voter, PoliticalParty

class VoterForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].choices = [
            ('', 'Select'),  # ✅ Replaces '---'
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other'),
        ]

class PoliticalPartyForm(forms.ModelForm):
    class Meta:
        model = PoliticalParty
        fields = '__all__'

class UIDForm(forms.Form):
    aadhar_number = forms.CharField(label='Enter Aadhaar Number', max_length=12)

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=8, label="Enter OTP")
