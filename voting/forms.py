from django import forms
from .models import Voter, PoliticalParty

class VoterForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = '__all__'
        widgets = {
            'face_image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
    def clean_aadhar_number(self):
        aadhar = self.cleaned_data.get('aadhar_number')
        if aadhar and len(aadhar) != 12:
            raise forms.ValidationError("Aadhaar number must be 12 digits")
        return aadhar

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone and len(phone) != 10:
            raise forms.ValidationError("Phone number must be 10 digits")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            existing_voter = Voter.objects.filter(email=email).first()
            if existing_voter:
                raise forms.ValidationError(f"This email is used by {existing_voter.name}")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'gender' in self.fields:  # safe check
            self.fields['gender'].choices = [
                ('', 'Select'),
                ('Male', 'Male'),
                ('Female', 'Female'),
                ('Other', 'Other'),
            ]

class PoliticalPartyForm(forms.ModelForm):
    class Meta:
        model = PoliticalParty
        fields = '__all__'

class UIDForm(forms.Form):
    aadhar_number = forms.CharField(
        label='Enter Aadhaar Number',
        max_length=12,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your 12-digit Aadhaar number'
        })
    )

class OTPForm(forms.Form):
    otp1 = forms.CharField(max_length=1, required=True, widget=forms.TextInput(attrs={'class': 'otp-input'}))
    otp2 = forms.CharField(max_length=1, required=True, widget=forms.TextInput(attrs={'class': 'otp-input'}))
    otp3 = forms.CharField(max_length=1, required=True, widget=forms.TextInput(attrs={'class': 'otp-input'}))
    otp4 = forms.CharField(max_length=1, required=True, widget=forms.TextInput(attrs={'class': 'otp-input'}))
    otp5 = forms.CharField(max_length=1, required=True, widget=forms.TextInput(attrs={'class': 'otp-input'}))
    otp6 = forms.CharField(max_length=1, required=True, widget=forms.TextInput(attrs={'class': 'otp-input'}))

    def get_otp(self):
        return ''.join([self.cleaned_data.get(f'otp{i}', '') for i in range(1, 7)])

    def clean(self):
        cleaned = super().clean()
        otp = self.get_otp()
        if not otp.isdigit() or len(otp) != 6:
            raise forms.ValidationError("OTP must be 6 digits")
        return cleaned
