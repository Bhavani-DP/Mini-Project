from django import forms

class UIDForm(forms.Form):
    uid = forms.CharField(label='Enter Aadhaar Number', max_length=12)

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=8, label="Enter OTP")

class VoteForm(forms.Form):
    party = forms.ChoiceField(widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', [])
        super().__init__(*args, **kwargs)
        self.fields['party'].choices = choices
